# word.py

'''
    Let's say that the PC is stored in r3:r2
    And the Frame Pointer (FP) is stored in Y
    And the Stack Pointer (SP) is stored in ??

    A Frame looks like:

    FP
    |
    V
    +------+------+----+----+----+----+----- ...
    | args | my   | calling | calling | vars ...
    |      | word | FP      | PC      |
    +------+------+----+----+----+----+----- ...

'''

PC = None         # PC of currently running function
FP = None         # FP of currently running function
SP = None         # SP of currently running thread

Data = [0] * (2 * 1024)
Flash = [0] * (15 * 1024)
Flash_end = 0

Wtable = []
Num_words = 0

def push_flash1(x):
    if Flash_end >= 15 * 1024:
        raise MemoryError("Out of Flash space")
    Flash[Flash_end] = x
    Flash_end += 1

def push_flash2(x):
    push_flash1(x & 0xff)
    push_flash1(x >> 8)

def push1(x):
    if SP >= 2 * 1024:
        raise MemoryError("Out of Data space")
    Data[SP] = x
    SP += 1

def push2(x):
    push1(x & 0xff)
    push1(x >> 8)

def pop1():
    if SP <= 0:
        raise SystemError("Data pop underflow")
    SP -= 1
    return Data[SP]

def pop2():
    return 256 * pop1() + pop1()

def get_data2(addr):
    return Data[addr] + 256 * Data[addr + 1]

def next():
    word = Wtable[Flash[PC]]
    PC += 1
    word.run()

def run():
    while (True) next()

class word(object):
    def __init__(self, name, min_args_len, max_args_len, ret_len):
        self.name = name
        self.min_args_len = min_args_len
        self.max_args_len = max_args_len
        self.ret_len = ret_len
        if Num_words >= 256:
            raise MemoryError("Word table full")
        self.word_index = Num_words
        Wtable[self.word_index] = self
        Num_words += 1
    def compile_value(self, compiler):
        compiler.push_call(self, self.min_args_len, self.max_args_len)
    def compile_lvalue(self, compiler):
        raise SyntaxError("illegal lvalue: %s" % self.name)
    def compile_cond(self, compiler):
        self.compile_value(compiler)
    def run(self):
        push1(self.word_index)
        push2(FP)
        push2(PC)
        FP = SP - self.args_len - 5
        PC = self.code_addr
        SP = FP + self.frame_size

class var_num_args(word):
    def run(self):
        arg_len_passed = Flash[PC]
        PC += 1
        SP += self.max_args_len - arg_len_passed
        super(var_num_args, self).run()

class lvalue(object):
    def __init__(self):
        deref(name, ret_len)
    def compile_value(self, compiler):
        push_flash1(self.word_index)
    def compile_lvalue(self, compiler):
        compiler.push_call(self, self.args_len, self.args_len)

