#!/usr/bin/env python3

# Liam Nolan (c) 2017
# BSD 2-Clause
# Full licence terms located in LICENCE file

from gphull.core import App

if __name__ == '__main__':
    try:
        a = App.App()
    except KeyboardInterrupt:
        raise
