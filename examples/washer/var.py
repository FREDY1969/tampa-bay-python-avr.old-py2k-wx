# var.py

from examples.washer import declaration

class var(declaration.word):
    def compile(self, db_cur):
        initial_value = self.get_answers(db_cur)['initial value'][0]
        data_name = self.name + "__data"
        return (("%s:" % self.name,
                 "    .code-addr do-var",
                 "    .data-addr %s" % data_name,
                ),
                ("%s:" % data_name,
                 "    .word %s" % initial_value,
                ),
                (),
                ('do-var',),
               )


