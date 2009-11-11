# assembler_word.py

from __future__ import with_statement

import itertools

from ucc.ast import ast, crud, symbol_table
from ucc.assembler import asm_opcodes
from ucclib.built_in import declaration

class assembler_word(declaration.word):
    def parse_file(self, parser):
        instructions = []
        filename = self.ww.get_filename()

        self.word_body_id = \
          symbol_table.symbol.create(self.name, self.ww.kind,
                                     source_filename=filename) \
            .id

        with open(filename) as f:
            for i, line in enumerate(f):
                inst = parse_asm(filename, line, i + 1)
                if inst: instructions.append(inst)
        with crud.db_transaction():
              ast.save_word(self.name, self.word_body_id, instructions)

    def compile(self, db_cur, words_by_name):
        insts = tuple(crud.read_as_tuples('ast',
                                          'label', 'word', 'str1', 'str2',
                                          kind='flash',
                                          word_body_id=self.word_body_id))
        my_labels = \
          frozenset(itertools.ifilter(None, itertools.imap(lambda x: x[0],
                                                           insts)))
        labels_used = \
          frozenset(
            itertools.imap(extract_label,
              itertools.ifilter(is_legal_label,
                itertools.chain(itertools.imap(lambda x: x[2], insts),
                                itertools.imap(lambda x: x[3], insts)))))
        return ((self.name, None, None, None),) + insts, (), (), (), \
               tuple(labels_used - my_labels)

def extract_label(operand):
    r'''Extract the label out of the operand.

    This is only fed operands that pass is_legal_label.

    >>> extract_label('mom')
    'mom'
    >>> extract_label('hi8(mom)')
    'mom'
    '''
    if '(' not in operand:
        return operand
    return operand[operand.index('(') + 1:operand.index(')')]

def is_legal_label(operand):
    r'''Determines whether operand is a legal label or not.

    >>> is_legal_label('mom')
    True
    >>> is_legal_label('r14')
    False
    >>> is_legal_label('Y+64')
    False
    >>> is_legal_label('X')
    False
    >>> is_legal_label('123')
    False
    >>> is_legal_label('0x23')
    False
    >>> is_legal_label("'x'")
    False
    >>> is_legal_label('"hi mom"')
    False
    >>> is_legal_label('io.spl')
    False
    '''
    if not operand: return False
    operand = operand.lower()
    if len(operand) >= 2 and operand[0] == 'r' and \
       operand[1:].isdigit() and 0 <= int(operand[1:]) <= 31:
        return False
    if len(operand) == 1 and operand in 'xyz' \
       or '+' in operand or '-' in operand:
        return False
    if operand[0].isdigit(): return False
    if operand[0] in "'\"": return False
    if operand.startswith('io.'): return False
    return True

def parse_asm(filename, line, lineno):
    r'''Parses one line of assembler code.  Returns ast node or None.
    '''
    stripped_line = line.rstrip()
    comment = stripped_line.find('#')
    if comment >= 0: stripped_line = stripped_line[:comment].rstrip()
    if not stripped_line: return None
    fields = stripped_line.split()
    label = opcode = None
    operands = ()
    if stripped_line[0] == ' ':
        if fields:
            opcode = fields[0]
            operands = ''.join(fields[1:]).split(',')
    else:
        if fields:
            label = fields[0]
            if len(fields) > 1:
                opcode = fields[1]
                operands = ''.join(fields[2:]).split(',')
    if len(operands) == 1 and not operands[0]: operands = ()
    if label is None and opcode is None and not operands: return None
    if len(operands) > 2:
        second_comma = line.find(',', line.find(',') + 1) + 1
        raise SyntaxError("no more than 2 operands are allowed",
                          (filename, lineno, second_comma, line))
    str1 = str2 = None
    if operands:
        str1 = operands[0]
    if len(operands) > 1:
        str2 = operands[1]
    int1 = int2 = 0
    if opcode is not None:
        inst_obj = getattr(asm_opcodes, opcode.upper(), None)
        if inst_obj is None:
            if label is not None:
                label_len = len(label)
                no_label = line[label_len:]
                opcode_column = \
                  label_len + len(no_label) - len(no_label.lstrip()) + 1
            else:
                opcode_column = len(line) - len(line.lstrip()) + 1
            raise SyntaxError("unknown opcode: %s" % opcode,
                              (filename, lineno, opcode_column, line))
        int1 = inst_obj.len
        if isinstance(inst_obj.cycles, int): int2 = inst_obj.cycles
        else: int2 = max(inst_obj.cycles)
    column_start = len(stripped_line) - len(stripped_line.lstrip()) + 1
    column_end = len(stripped_line)
    return ast.ast.from_parser((lineno, column_start, lineno, column_end),
                               kind = 'flash', label = label, word = opcode,
                               str1 = str1, str2 = str2,
                               int1 = int1, int2 = int2)

