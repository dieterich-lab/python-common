#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Printdots(object):

    def __init__(self, default = ".", columns = 80, frequency = 1):
        """"""
        def _set_int(value):
            try: return int(value)
            except ValueError as e:
                err = "Parameter must be an integer. (value = {V})".format(V = value)
                raise ValueError(err)
        
        self.default        = default
        self.frequency      = _set_int(frequency)
        self.max_columns    = _set_int(columns)
        self.count          = 0
        self.printed_column = 0
        
    def dot(self, symbol = False, columns = False, frequency = False):  
        _symbol = symbol if symbol else self.default 
        self.frequency = frequency if frequency else self.frequency
        self.max_columns = columns if columns else self.max_columns
           
        if self.count % self.frequency == 0:
            print(_symbol, end="")
            self.count += 1
            self.printed_column += 1
            
            if self.printed_column > self.max_columns:
                print() # Newline
                self.printed_column = 0

if __name__ == '__main__':
    dots = Printdots(columns = 20)  
    for i in range(1,100,1):
        dots.dot()
    for i in range(1,10,1):
        dots.dot("S")
    for i in range(1,100,1):
        dots.dot()
