# number.py

import math

class fixed_precision(object):
    def __init__(self, str, base = 10):
        if '~' not in str:
            if '.' not in str:
                n = base * int(str, base)
                precision = 0.5
                decimal_pt = 0
            else:
                dot = str.index('.')
                i = int(str[:dot], base)
                n = int(str[dot+1:], base)
                decimal_pt = len(str) - dot - 1
                n += i * base**decimal_pt
                precision = 0.5
        else:
            tilde = str.index('~')
            assert tilde + 1 < len(str), \
                   "missing precision after '~' in approx number"
            if '.' not in str:
                n = int(str[:tilde], base)
                precision = float(int(str[tilde + 1:], base))
                decimal_pt = -(len(str) - tilde - 2)
                n *= base**-decimal_pt
                precision *= base**decimal_pt
            else:
                dot = str.index('.')
                assert dot < tilde, "'.' after '~' in approx number"
                i = int(str[:dot], base)
                n = int(str[dot+1:tilde], base)
                decimal_pt = tilde - dot - 1
                n += i * base**decimal_pt
                precision = float(int(str[tilde + 1:], base))
                precision /= base**(len(str) - tilde - 2)
        self.binary_pt = int(math.ceil(math.log(base, 2)*decimal_pt
                                        - math.log(precision, 2)))
        self.i = int(round(float(n) *
                             float(2**self.binary_pt) / base**decimal_pt))
    def __repr__(self):
        if self.binary_pt < 0:
            return "%r~%r" % (self.i, 2**-(self.binary_pt - 1))
        if self.binary_pt == 0:
            return "%r" % (self.i,)
        # 2**self.binary_pt = 10**decimal_pt / precision
        decimal_pt = int(math.ceil(self.binary_pt / math.log(10, 2)))
        n = self.i * 2**-self.binary_pt
        n1 = round(n, decimal_pt)
        precision = int(round(10.0**decimal_pt / 2**self.binary_pt))
        return "%s~%r" % (n1, precision)
    def to_domain(self):
        return domain.constant(self,
                               domain.fixed_precision(self, self,
                                                      self.binary_pt,
                                                      self.binary_pt))

class any_precision(object):
    def __init__(self, str, base = 10):
        assert '/' in str, "missing '/' in exact number"
        slash = str.index('/')
        if '.' not in str:
            self.numerator = int(str[:slash], base)
            if slash + 1 == len(str):
                self.denominator = 1
            else:
                self.denominator = int(str[slash + 1:], base)
        else:
            dot = str.index('.')
            assert dot < slash, "'.' after '/' in exact number"
            i = int(str[:dot], base)
            n = int(str[dot+1:slash], base)
            if slash + 1 == len(str):
                self.denominator = base**(slash - dot - 1)
            else:
                self.denominator = int(str[slash + 1:], base)
            self.numerator = i * self.denominator + n
    def __repr__(self):
        i = self.numerator // self.denominator
        if i == 0:
            return "%r/%r" % (self.numerator, self.denominator)
        r = self.numerator - self.denominator * i
        if r == 0:
            return "%r/" % (i,)
        l = math.log10(self.denominator)
        if abs(l - round(l)) < 1e-9:
            rs = "%r" % r
            return "%r.%s%s/" % (i, '0' * (int(round(l)) - len(rs)), rs)
        return "%r.%r/%r" % (i, r, self.denominator)
    def to_domain(self):
        return domain.constant(self, domain.any_precision(self, self))

