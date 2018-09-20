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
def file_type(pathname):
    '''
    custom type for checking a file exists
    '''
    if path.isfile(pathname) is True:
        return pathname
    return None
def expire_range(num):
    '''
    type for checking source url query timeout 'expiry'
    can be set from '1' sec (not a good idea!) to '315328464000'
    '''
    if num >= 1.0 and num <= 315328464000.0:
        return num
    return None

def sqlite3_cursor_type(cursor):
    '''
    checks to see if passed argument is a sqlite3.Cursor
    returns cursor if valid, None otherwise
    '''
    if type(cursor) == Cursor:
        return cursor
    return None

def log_level_type(level):
    '''
    defines 3 logging levels
    - debug: verbose informational messages
    - notice: normal operating messages
    - critical: errors only
    '''
    levels = ('debug', 'notice', 'critical')
    if level in levels:
        return level
    return None

def format_type(string):
    '''
    returns input if the input string matches
    a supported data type OLD
    '''
    if string in list(Data.VALIDATOR)[0]:
        return string
    return None
    
def frequency_range(integer):
    '''
    type for argparse returns true for a positive integer
    '''
    if integer is int and integer > 0:
        return integer
    return None
