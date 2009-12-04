# block.py

import collections
from ucc.database import crud, fn_xref, symbol_table, triple

Current_block = None

Block_ids = {}                                        # {block_name: block_id}

def new_label(name, word_symbol_id):
    global Current_block
    if Current_block:
        if Current_block.state == 'end_fall_through':
            Current_block.write(name)
        if Current_block.state == 'end_absolute':
            Current_block.write()
        else:
            Current_block.unconditional_to(name)
    block(name, word_symbol_id)

class block(object):
    last_triple = None
    next_conditional = None

    def __init__(self, name, word_symbol_id):
        global Current_block

        assert not Current_block, \
               "%s: previous block(%s) not written" % (name, Current_block.name)

        self.name = name
        self.word_symbol_id = word_symbol_id

        # The final labels left in this dict when the block is written are
        # added as labels to the indicated triples.  These can be either
        # global or local (including parameter) variables.
        #
        # Each time a 'set' is done to a variable, the triple setting that
        # variable is updated (replacing any previous triple).  So at any
        # point in time, the triple in this dict is the last one to set the
        # indicated variable.
        #
        # When a triple is associated with a global variable that is used
        # indirectly by a subsequent triple, the global variable is added to
        # the first triple's labels list.  Thus, these triples will always
        # store to the global variable, even if a later triple also stores
        # to that global variable.
        #
        # All triples here are written to the database when the block write is
        # done.
        self.labels = {}             # {symbol_id: triple}

        # This is used to find previous triples that are duplicates of the
        # triple being created.  Information here is never changed or deleted.
        # But not all triples here may be written out at the end...
        self.triples = {}            # {(operator, int1, int2, string): triple}

        # This stores the last triple that has side effects.  When a new
        # triple comes along that also has side effects, a dependency is
        # established between them to guarantee that the side effects happen
        # in the proper sequence.  The last triple here is always included in
        # the final block write to the database.
        self.side_effects = None

        # The triples that use each global variable since the last time it was
        # set.
        #
        # When a new triple is added that sets a global variable, a dependency
        # is established between each of the triples here and the new triple
        # to ensure that the new triple doesn't run until after all of the
        # triples here have run.  These are "soft" dependencies that are not
        # enough, in themselves, to cause the triples here to be written to
        # the database when the final block write is done.
        #
        # Each time a new triple is created that sets a global variable, this
        # entry is cleared (after creating the above dependencies).
        #
        # Triples in this dict may not be written to the database when the
        # block write is done.
        #
        # This dict is: {symbol_id: [triple]}
        self.uses_global = collections.defaultdict(list)

        # The triple the last set each global variable.  When a new triple is
        # created that uses or sets a global variable, a "hard" dependency is
        # created between this triple and the new triple.
        #
        # These triples will always be written to the database when the final
        # block write is done.
        self.sets_global = {}        # {symbol_id: triple}

        self.state = 'not_ended'

        Current_block = self

    def __repr__(self):
        return "<block %s>" % self.name

    def more(self):
        global Current_block
        assert self.state != 'end_absolute', \
               "%s: block missing label after jump" % self.name
        if self.state == 'end_fall_through':
            name = crud.gensym('block')
            self.write(name)
            Current_block = block(name, self.word_symbol_id)
            return True
        return False

    def true_to(self, cond_id, name_t):
        r'''Branch to name_t if cond_id is true.
        
        False falls through.
        '''
        if self.more(): Current_block.true_to(cond_id, name_t)
        else:
            self.last_triple = triple.triple('if-true', cond_id, string=name_t)
            self.next_conditional = name_t
            self.state = 'end_fall_through'

    def false_to(self, cond_id, name_f):
        if self.more(): Current_block.false_to(cond_id, name_f)
        else:
            self.last_triple = triple.triple('if-false', cond_id, string=name_f)
            self.next_conditional = name_f
            self.state = 'end_fall_through'

    def unconditional_to(self, name):
        if self.more(): Current_block.unconditional_to(name)
        else:
            self.state = 'end_fall_through'
            self.write(name)

    def block_end(self, last_triple):
        assert self.state == 'not_ended', \
               "%s: double block end" % self.name
        self.state = 'end_absolute'
        self.last_triple = last_triple
        self.write()

    def gen_triple(self, operator, int1=None, int2=None, string=None,
                         syntax_position_info=None):
        #print self.name, "gen_triple", operator, int1, int2, string
        if self.more():
            return Current_block.gen_triple(operator, int1, int2, string,
                                            syntax_position_info)
        if operator in ('global', 'local'):
            if int1 in self.labels: return self.labels[int1]
        if operator == 'call_direct':
            assert isinstance(int1, symbol_table.symbol)
            fn_symbol = int1
            ans = triple.triple(operator, fn_symbol, int2, string,
                                syntax_position_info)
            uses_vars, sets_vars = fn_xref.get_var_uses(fn_symbol.id)
            for var_id in uses_vars.intersection(self.labels):
                self.labels[var_id].add_label(var_id)
            if fn_symbol.side_effects:
                if self.side_effects is not None:
                    ans.add_hard_predecessor(self.side_effects)
                self.side_effects = ans
            for var_id in sets_vars.intersection(self.uses_global):
                for t in self.uses_global[var_id]:
                    ans.add_soft_predecessor(t)
                del self.uses_global[var_id]
            for var_id \
             in uses_vars.union(sets_vars).intersection(self.sets_global):
                ans.add_hard_dependency(self.sets_global[var_id])
            for var_id in uses_vars:
                self.uses_global[var_id].append(ans)
            for var_id in sets_vars:
                self.sets_global[var_id] = ans
                if var_id in self.labels: del self.labels[var_id]
            return ans
        if operator == 'call_indirect':
            raise AssertionError("call_indirect not yet implemented")
        if operator not in ('param', 'input', 'input-bit',
                            'output', 'output-bit-set', 'output-bit-clear',
                            'var_data', 'const_data', 'bss', 'ioreg_init',
                            'eeprom'):
            key = operator, int1, int2, string
            if key not in self.triples:
                self.triples[key] = triple.triple(operator, int1, int2, string,
                                                  syntax_position_info)
            return self.triples[key]
        ans = triple.triple(operator, int1, int2, string, syntax_position_info)
        if operator == 'global':
            self.uses_global[int1].append(ans)
        if operator in ('input', 'input-bit',
                        'output', 'output-bit-set', 'output-bit-clear'):
            #print self.name, "got", operator, "storing in side_effects"
            if self.side_effects is not None:
                ans.add_hard_predecessor(self.side_effects)
            self.side_effects = ans
        return ans

    def label(self, symbol_id, triple):
        self.labels[symbol_id] = triple

    def write(self, next = None):
        r'''Writes the block and triples to the database.

        Returns the id assigned to the block.
        '''

        global Current_block

        #print self.name, "write"

        if self.state == 'end_absolute':
            next = None
        else:
            assert next is not None

        id = crud.insert('blocks',
                         name=self.name,
                         word_symbol_id=self.word_symbol_id,
                         last_triple_id=self.last_triple.id
                                          if self.last_triple
                                          else None,
                         next=next,
                         next_conditional=self.next_conditional)

        # add final labels to their associated triples:
        for var_id, t in self.labels.iteritems():
            t.add_label(var_id)

        # write out triples:
        #
        # first figure out the set of all triples that will be forcably
        # written:
        forced_triples = set(self.labels.values())
        if self.side_effects is not None:
            #print self.name, "adding", self.side_effects, "due to side_effects"
            forced_triples.add(self.side_effects)
        forced_triples.update(self.sets_global.values())
        if self.last_triple is not None:
            #print self.name, "adding", self.last_triple, "as last_triple"
            forced_triples.add(self.last_triple)
        #
        # then write them all:
        #
        for t in forced_triples:
            t.write(id)
        #
        # then call write_soft_predecessors for all of them:
        #
        for t in forced_triples:
            t.write_soft_predecessors(id)

        assert self.name not in Block_ids
        Block_ids[self.name] = id

        Current_block = None
        #print self.name, "write returning", id
        return id

