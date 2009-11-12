# compile.py

from __future__ import with_statement

import sys
import os.path
import itertools
import traceback

from ucc.word import helpers, xml_access, word
from ucc.parser import genparser
from ucc.ast import ast, crud, symbol_table
from ucc.assembler import assemble
from ucclib.built_in import declaration

Built_in = 'ucclib.built_in'

Debug = 0

def load_word(ww):
    r'''Loads and returns the word_obj for ww.
    
    And updates Word_objs_by_label, Rules and Token_dict.
    '''
    global Word_objs_by_label, Rules, Token_dict
    if ww.label not in Word_objs_by_label:
        if not ww.is_root():
            load_word(ww.kind_obj)

        # load new_word
        if ww.is_root():
            assert ww.defining, \
                   "%s: root word that is not a defining word" % ww.label
            new_word = declaration.load_class(ww)
        elif ww.defining:
            new_word = Word_objs_by_label[ww.kind_obj.label].create_subclass(ww)
        else:
            new_word = Word_objs_by_label[ww.kind_obj.label](ww)

        # get new_syntax
        if ww.defining:
            new_syntax = new_word.new_syntax()
            if new_syntax:
                r, td = new_syntax
                Rules.extend(r)
                Token_dict.update(td)

        # Add new word to Word_objs_by_label
        Word_objs_by_label[ww.label] = new_word
        return new_word
    return Word_objs_by_label[ww.label]

def create_parsers(top):
    r'''Creates a parser in each package.

    Returns {package_name: parser module}

    Also does load_word on all of the defining words.
    '''
    global Rules, Token_dict

    Rules = []
    Token_dict = {}
    package_parsers = {}
    syntax_file = os.path.join(os.path.dirname(__file__), 'SYNTAX')
    for p in top.packages:
        for ww in p.get_words():
            ww.symbol_id = \
              symbol_table.symbol.create(ww.label, ww.kind,
                                         source_filename=ww.get_filename()) \
                .id
            load_word(ww)

        #print "Rules", Rules
        #print "Token_dict", Token_dict

        # compile new parser for this package:
        with open(os.path.join(p.package_dir, 'parser.py'), 'w') as output_file:
            genparser.genparser(syntax_file, '\n'.join(Rules), Token_dict,
                                output_file)

        # import needed modules from the package:
        package_parsers[p.package_name] = \
          helpers.import_module(p.package_name + '.parser')
    return package_parsers

def parse_word(ww, word_obj, parser):
    r'''Parses the word with the parser.

    Return True on success, False on failure.

    Catches exceptions and prints its own error messages.

    This needs an crud.db_connection open.
    '''
    try:
        if not isinstance(word_obj, type): # word_obj not a class
            word_obj.parse_file(parser, Debug)
    except SyntaxError:
        e_type, e_value, e_tb = sys.exc_info()
        for line in traceback.format_exception_only(e_type, e_value):
            sys.stderr.write(line)
        return False
    except Exception:
        traceback.print_exc()
        return False
    return True

def parse_needed_words():
    pass

def gen_intermediate_code():
    pass

def optimize():
    pass

def gen_assembler():
    pass

def run(top):
    global Word_objs_by_label

    # The following gets a little confusing because we have two kinds of word
    # objects:
    #
    #   1.  ww objects       ("word_word", i.e., instances of the
    #                         ucc.word.word.word class)
    #   2.  word_obj objects (either subclasses or instances of the
    #                         ucclib.built_in.declaration.declaration class)
    #

    # Gather Word_objs_by_label, and build the parsers for each package:
    Word_objs_by_label = {}  # {word.label: word_obj}

    with crud.db_connection(top.packages[-1].package_dir):

        # {package_name: parser module}
        with crud.db_transaction():
            package_parsers = create_parsers(top)  # Also loads all of the
                                                   # word objs

        # parse files in the package:
        flash = []      # list of (label, opcode, operand1, operand2)
        data = []       # list of (label, datatype, operand)
        bss = []        # list of (label, num_bytes)
        eeprom = []     # list of (label, datatype, operand)
        words_done = set()
        words_needed = set(['startup'])
        num_errors = 0
        while words_needed:
            next_word = words_needed.pop()
            ww = top.get_word_by_name(next_word)
            word_obj = Word_objs_by_label[ww.label]
            if parse_word(ww, word_obj, package_parsers[ww.package_name]):
                with crud.db_transaction():
                    f, d, b, e, n = word_obj.compile(Word_objs_by_label)
                flash.extend(f)
                data.extend(d)
                bss.extend(b)
                eeprom.extend(e)
                words_done.add(next_word)
                words_needed.update(frozenset(n) - words_done)
            else:
                num_errors += 1

        if num_errors:
            sys.stderr.write("%s files had syntax errors\n" % num_errors)
            sys.exit(1)

        gen_intermediate_code()
        optimize()
        gen_assembler()

        #print "flash", flash
        #print "data", data
        #print "bss", bss
        #print "eeprom", eeprom

        with open(os.path.join(top.packages[-1].package_dir, 'flash.hex'),
                  'w') \
          as flash_file:
            insts = assemble.assemble(flash)
            for i in itertools.count():
                data_hex = ''.join(itertools.imap(
                                     lambda n: "%04x" % byte_reverse(n),
                                     itertools.islice(insts, 8)))
                if not data_hex: break
                line = "%02x%04x00%s" % (len(data_hex)/2, i * 16, data_hex)
                flash_file.write(":%s%02x\r\n" % (line, check_sum(line)))
                if len(data_hex) < 32: break
            assert not data
            assert not bss
            flash_file.write(":00000001FF\r\n")
        assert not eeprom

def byte_reverse(n):
    r'''Reverses the two bytes in a 16 bit number.

    >>> hex(byte_reverse(0x1234))
    '0x3412'
    '''
    return ((n << 8) & 0xff00) | (n >> 8)

def check_sum(data):
    r'''Calculates the .hex checksum.

    >>> hex(check_sum('100000000C9445010C9467110C9494110C946D01'))
    '0x9f'
    >>> hex(check_sum('10008000202D2068656C70202874686973206F75'))
    '0x56'
    '''
    sum = 0
    for i in range(0, len(data), 2):
        sum += int(data[i:i+2], 16)
    return (256 - (sum & 0xff)) & 0xFF

