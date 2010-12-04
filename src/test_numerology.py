#!/usr/bin/env python
#-*- coding:cp1251 -*-

import unittest
import string
import random
import numerology

class TestConvertFunctions(unittest.TestCase):
    __ALPHA_NUM = (
    (' ', 0),
    ('A', 1),
    ('B', 2),
    ('C', 3),
    ('Y', 25),
    ('Z', 26),
    )

    def test_alpha_to_int(self):
        for alpha, num in self.__ALPHA_NUM:
            print alpha, num
            res = numerology.alpha_to_int(alpha)
            self.assertEqual(num, res) 

    def test_int_to_alpha(self):
        for alpha, num in self.__ALPHA_NUM:
            self.assertEqual(alpha, numerology.int_to_alpha(num))

    def test_sanity(self):
        nums = [random.randint(0, 26) for x in range(100)] 
        alphs = map(numerology.int_to_alpha, nums)
        self.assertEqual(nums, map(numerology.alpha_to_int, alphs))
    
    def test_fuzzy(self):
        caps = [string.uppercase[random.randint(0,len(string.uppercase)-1)] for x in range(100)]
        lows = [x.lower() for x in caps]
        for cap, low in zip(caps, lows):
            self.assertEqual(numerology.alpha_to_int(cap), numerology.alpha_to_int(low))
        
    def test_errors(self):
        self.assertRaises(numerology.WrongCharError, numerology.alpha_to_int, '-')
        self.assertRaises(numerology.WrongIntegerError, numerology.int_to_alpha, -1)

if __name__=="__main__":
    unittest.main()