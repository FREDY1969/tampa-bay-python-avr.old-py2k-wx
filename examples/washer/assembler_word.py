# assembler_word.py

from __future__ import with_statement

import os.path
from ucc.ast import ast
from ucc.assembler import asm_opcodes
from examples.washer import declaration

class assembler_word(declaration.declaration):
    def parse_file(self, parser, filename):
        name = os.path.basename(filename)
        assert name.endswith('.asm')
        name = name[:-4]
        with ast.db_transaction() as db_cur:
            ast.delete_word_by_name(name)
            instructions = []
            with open(filename) as f:
                for i, line in enumerate(f):
                    inst = parse_asm(filename, line, i + 1)
                    if inst: instructions.append(inst)
            root = ast.ast(kind='word_body', word=name, str1=filename,
                           *instructions)
            root.save(db_cur)

def parse_asm(filename, line, lineno):
    r'''Parses one line of assembler code.  Returns ast node or None.
    '''
    stripped_line = line.rstrip()
    comment = stripped_line.find('#')
    if comment >= 0: stripped_line = stripped_line[:comment].rstrip()
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
                               label = label, word = opcode,
                               str1 = str1, str2 = str2,
                               int1 = int1, int2 = int2)

