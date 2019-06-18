#!/usr/bin/env python3
# Liam Nolan 2018 (c) ISC

import unittest
from bdigester.core import Parser 

class TestParser(unittest.TestCase):
    def TestFindABP(self):
         with open('data/easylist.txt', 'r') as testdata:
             for line in Parser.find_abp_data(testdata):
                 print(line)


if __name__ == '__main__':
    unittest.main()


