#!/usr/bin/env python

# compile.py project_dir

from __future__ import with_statement

import sys
import os, os.path
import contextlib
import itertools
import traceback
import sqlite3 as db
import setpath

#print "__file__", __file__
python_path = setpath.setpath(__file__)
print "python_path", python_path

from ucc.word import helpers, xml_access, word
from ucc.parser import genparser
from ucc.ast import ast
from ucc.assembler import assemble

def usage():
    sys.stderr.write("usage: compile.py project_dir\n")
    sys.exit(2)

def run():
    if len(sys.argv) != 2: usage()

    project_dir = sys.argv[1]

    # Figure out python package name for project.
    abs_project_dir = os.path.abspath(project_dir)
    assert abs_project_dir.startswith(python_path)
    project_pkg = abs_project_dir[len(python_path) + 1:] \
                    .replace(os.path.sep, '.')
    if os.path.sep != '/': project_pkg.replace('/', '.')

    # Gather words_by_name, rules and token_dict:

    mod = helpers.import_module(project_pkg, 'declaration')
    decl = getattr(mod, 'declaration')
    decl.init_class('declaration', 'declaration', project_dir)
    words_by_name = {'declaration': decl}
    rules = ()
    token_dict = {}

    word_names = xml_access.read_word_list(project_dir)[1]

    # Load word objects and defining words, create translation_dict:
    word_words = []  # list of word.word objects
    translation_dict = {}
    for name in word_names:
        word_obj = word.read_word(name, project_dir)
        word_words.append(word_obj)
        if word_obj.name != word_obj.label:
            translation_dict[word_obj.label] = word_obj.name
        if word_obj.defining:
            #print "defining:", name, word_obj.kind
            new_word, new_syntax = \
              words_by_name[word_obj.kind].create_instance(project_pkg, name,
                                                           word_obj.label,
                                                           project_dir)
            if new_syntax:
                r, td = new_syntax
                rules += r
                token_dict.update(td)
            words_by_name[name] = new_word

    ast.Translation_dict = translation_dict

    # Load non-defining words:
    for w in word_words:
        if not w.defining:
            #print "non-defining", w.name, w.kind
            new_word, new_syntax = \
              words_by_name[w.kind].create_instance(project_pkg, w.name,
                                                    w.label, project_dir)
            if new_syntax:
                r, td = new_syntax
                rules += r
                token_dict.update(td)
            words_by_name[w.name] = new_word

    #print "rules", rules
    #print "token_dict", token_dict

    # compile new parser for this project:
    with open(os.path.join(project_dir, 'parser.py'), 'w') as output_file:
        genparser.genparser(os.path.join(os.path.dirname(__file__), 'SYNTAX'),
                            '\n'.join(rules), token_dict, output_file)

    # import needed modules from the project:
    parser = helpers.import_module(project_pkg, 'parser')

    # parse files in the project:
    num_errors = 0
    with ast.db_connection(project_dir):
        for word_obj in words_by_name.itervalues():
            #print "final loop", word_obj
            try:
                if not isinstance(word_obj, type): # word_obj not a class
                    word_obj.parse_file(parser, project_dir)
            except SyntaxError:
                e_type, e_value, e_tb = sys.exc_info()
                for line in traceback.format_exception_only(e_type, e_value):
                    sys.stderr.write(line)
                num_errors += 1
            except Exception:
                traceback.print_exc()
                num_errors += 1
        if num_errors:
            sys.stderr.write("%s files had syntax errors\n" % num_errors)
            sys.exit(1)

        flash = []      # list of (label, opcode, operand1, operand2)
        data = []       # list of (label, datatype, operand)
        bss = []        # list of (label, num_bytes)
        eeprom = []     # list of (label, datatype, operand)
        words_done = set()
        words_needed = set(['startup'])
        while words_needed:
            next_word = words_needed.pop()
            with ast.db_transaction() as db_cur:
                f, d, b, e, n = \
                  words_by_name[next_word].compile(db_cur, words_by_name)
            flash.extend(f)
            data.extend(d)
            bss.extend(b)
            eeprom.extend(e)
            words_done.add(next_word)
            words_needed.update(frozenset(n) - words_done)
        #print "flash", flash
        #print "data", data
        #print "bss", bss
        #print "eeprom", eeprom
        with open(os.path.join(project_dir, 'flash.hex'), 'w') as flash_file:
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

if __name__ == "__main__":
    run()
