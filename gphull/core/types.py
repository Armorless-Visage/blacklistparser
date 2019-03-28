#!/usr/bin/env python3

# Liam Nolan (c) 2018 ISC
# Full licence terms located in LICENCE file

from os import path
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
