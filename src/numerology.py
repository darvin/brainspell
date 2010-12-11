#-*- coding:cp1251 -*-
from string import ascii_uppercase

MAX_NUMBER = 26
MIN_NUMBER = 0

class WrongCharError(Exception):
    pass

class WrongIntegerError(Exception):
    pass

def alpha_to_int(alpha):
    try:
        return ascii_uppercase.index(alpha.upper())+1
    except ValueError:
        if alpha == ' ':
            return 0
        else:
            raise WrongCharError

def int_to_alpha(num):
    
    if num==0:
        return ' '
    elif MIN_NUMBER<num<=MAX_NUMBER:
        return ascii_uppercase[num-1]
    else:
        raise WrongIntegerError
    