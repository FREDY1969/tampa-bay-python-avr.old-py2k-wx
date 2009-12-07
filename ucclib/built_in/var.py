# var.py

from ucc.database import assembler, block
from ucclib.built_in import declaration

class var(declaration.word):
    def compile(self):
        initial_value = self.ww.get_value('initial_value')
        if initial_value is None:
            block = assembler.block('bss', self.name)
            block.append_inst('zeroes', '2')
            block.write()
        else:
            block = assembler.block('data', self.name)
            block.append_inst('int16', str(initial_value))
            block.write()

    def compile_value(self, ast_node):
        return block.Current_block.gen_triple('global', self.ww.symbol)

