#!/usr/bin/env python3

# Liam Nolan (c) 2017
# BSD 2-Clause
# Full licence terms located in LICENCE file

from blacklistparser.core import App

if __name__ == '__main__':
    try:
        App.App()
    except KeyboardInterrupt:
        raise
