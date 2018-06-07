#!/usr/bin/env python3
# Liam Nolan 2018 (c) ISC

import unittest
from bdigester.core import Parser

def test():
    with open('gphull/tests/data/easylist.txt', 'r') as testdata:
        print("begin")
        try:
            matches = Parser.find_abp_data(testdata.read())
        except:
            raise
        if matches:
            print("matches found")
            for each in matches:
                print(each)


if __name__ == '__main__':
    test()


