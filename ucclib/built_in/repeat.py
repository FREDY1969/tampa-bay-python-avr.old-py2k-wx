# repeat.py

r'''Repeat statement.

This is implemented as a macro.
'''

from ucc.database import ast, crud, symbol_table
from ucclib.built_in import macro

class repeat(macro.macro):
    def macro_expand(self, fn_symbol, ast_node, words_needed):
        #print "repeat.macro_expand"
        _, count, body = ast_node.args
        loop_label = crud.gensym('repeat')
        if not count:
            #print "no count"
            new_args = (
              ast.ast(kind='label', label=loop_label, expect='statement'),
              body,
              ast.ast(kind='jump', label=loop_label, expect='statement'),
            )
        else:
            count = count[0]
            #print "count", count
            if count.kind == 'int':
                assert count.int1 >= 0, \
                       "repeat must not have negative repeat count"
                if count.int1 == 0:
                    return ast_node.macro_expand(fn_symbol, words_needed, (),
                                                 kind='no-op')
                if count.int1 == 1:
                    return ast_node.macro_expand(fn_symbol, words_needed, body,
                                                 kind='series')
                first_jmp = ()
            else:
                first_jmp = (
                    ast.ast(kind='jump', label=test, expect='statement'),
                )

            loop_var = crud.gensym('repeat_var')
            symbol_id = \
              symbol_table.symbol.create(loop_var, 'var', fn_symbol).id
            test = crud.gensym('repeat_test')
            new_args = (
              ast.ast(ast.ast.word(symbol_table.get('set').id),
                      (ast.ast.word(symbol_id),
                       count,
                      ),
                      kind='call',
                      expect='statement') \
                 .prepare(fn_symbol, words_needed),
            ) + first_jmp + (
              ast.ast(kind='label', label=loop_label, expect='statement'),
            ) + body + (
              ast.ast(ast.ast.word(symbol_table.get('set').id),
                      (ast.ast.word(symbol_id),
                       ast.ast(ast.ast.word(symbol_table.get('-').id),
                               ast.ast.word(symbol_id),
                               ast.ast(kind='int', int1=1),
                               kind='call',
                              ) \
                          .prepare(fn_symbol, words_needed),
                      ),
                      kind='call',
                      expect='statement') \
                 .prepare(fn_symbol, words_needed),
              ast.ast(kind='label', label=test, expect='statement'),
              ast.ast(ast.ast.word(symbol_id, expect='condition'),
                      kind='if-true',
                      label=loop_label,
                      expect='statement'),
            )

        return ast_node.macro_expand(fn_symbol, words_needed, new_args,
                                     kind='series')

