#!/usr/bin/env python3

# Liam Nolan (c) 2018 ISC
# Full licence terms located in LICENCE file

from os import path
from sqlite3 import Cursor
from gphull.core import Data


'''
some types for argparse type argument
'''

def base_path_type(pathname):
    '''
    custom type for checking that a file path is valid
    returns input if the base dir exists, None otherwise
    '''
    if path.isdir(path.dirname(pathname)) is True:
        return pathname
    return None
def dir_type(pathname):
    '''
    custom type for checking a directory exists
    '''
    if path.isdir(pathname) is True:
        return pathname
    return None

def format_type(string):
    '''
    returns input if the input string matches
    a supported data type OLD
    '''
    if string in list(Data.VALIDATOR)[0]:
        return string
    return None
