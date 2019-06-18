#!/usr/bin/env python3
# Liam Nolan 2018 (c) ISC

import unittest
from gphull.core import Parser, Data

def test():
    with open('bdigester/tests/data/easylist.txt', 'r') as testdata:
        print("begin")
        try:
            matches = Data.DataList(testdata.read())
        except:
            raise
        if matches:
            print("matches found")
            for each in matches:
                print(each)
                


if __name__ == '__main__':
    test()


