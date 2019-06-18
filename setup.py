#!/usr/bin/env python3
# Liam Nolan (c) 2019 ISC

from distutils.core import setup

setup(
        name='blacklistparser',
        version='0.1.0.dev12',
        description='ip/domain blacklist management tool',
        author='Liam Nolan',
        author_email='Armorless-Visage@users.noreply.github.com',
        url='https://github.com/Armorless-Visage/blacklistparser',
        packages=['blacklistparser', 'blacklistparser.core'],
        classifiers=[
            'Intended Audience :: System Administrators',
            'Operating System :: BSD :: OpenBSD',
            'Operating System :: LSB :: Fedora',
            'Topic :: Systems Administration :: Firewall',
            'Topic :: Systems Administration :: Blacklist'],
        license='ISC'
        )
