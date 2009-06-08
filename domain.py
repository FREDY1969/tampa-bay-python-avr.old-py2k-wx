# domain.py

class domain(object):
    def type(self): return self.__class__.__name__

class type(domain):
    def __init__(self, max, min = 0):
        self.max = max
        self.min = min

class number(type):
    def __init__(self, max, min = 0, binary_pt = 0):
        super(number, self).__init__(max, min)
        self.binary_pt = binary_pt

class exact_number(number):
    pass

class approx_number(number):
    def __init__(self, max, min, binary_pt, precision):
        super(approx_number, self).__init__(max, min, binary_pt)
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

byte = exact_number(2**8 - 1)
int = exact_number(2**15 - 1, -(2**15))
uint = exact_number(2**16 - 1)
long = exact_number(2**31 - 1, -(2**31))
ulong = exact_number(2**32 - 1)
