# domain.py

class domain(object):
    def type(self): return self.__class__.__name__

class type(domain):
    def __init__(self, max, min = 0):
        self.max = max
        self.min = min

class number(type):
    pass

class any_precision(number):
    pass

class fixed_precision(number):
    def __init__(self, max, min, binary_pt, precision):
        super(approx_number, self).__init__(max, min)
        self.binary_pt = binary_pt
        self.precision = precision

class array(type):
    r''' Max, min refer to the length of the array. '''
    def __init__(self, max, min, element_type):
        super(array, self).__init__(max, min)
        self.element_type = element_type

class Parray(array):
    pass

class string(array):
    r''' Max, min refer to the length of the string. '''
    def __init__(self, max, min):
        super(string, self).__init__(max, min, byte)

class Pstring(string, Parray):
    pass

class constant(domain):
    def __init__(self, value, type):
        self.value = value
        self.type = type
        if isinstance(type, number):
            type.max = type.min = value
        elif isinstance(type, (string, array)):
            type.max = type.min = len(value)

int1 = exact_number(2**7 - 1, -(2**7))
uint1 = byte = exact_number(2**8 - 1)
int2 = exact_number(2**15 - 1, -(2**15))
uint2 = exact_number(2**16 - 1)
int3 = exact_number(2**23 - 1, -(2**23))
uint3 = exact_number(2**24 - 1)
int4 = exact_number(2**31 - 1, -(2**31))
uint4 = exact_number(2**32 - 1)
