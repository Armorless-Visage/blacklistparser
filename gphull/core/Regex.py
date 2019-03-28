#!/usr/bin/env python3
# Liam Nolan (c) 2018 ISC

import re

'''
base regex patterns for matching domains and ips modified from
Regular Expressions Cookbook
2nd Edition by Steven Levithan, Jan Goyvaerts
\b((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,63}\b
^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$
'''

DOMAIN_REGEX = re.compile(r'\b((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,63}\b')
ABP_DOMAIN = re.compile(r'^(?:\|\|)(((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,63})(?:\^(\$third-party)?)$')
ABP_DOMAIN_NOTHIRD = re.compile(r'^(?:\|\|)(((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,63})(?:\^)$')
ABP_VERSION = re.compile(r'^\[Adblock Plus 2\.0\]$')
NEWLINE_DOMAIN = re.compile(r'^(((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,63})$')
IPV4_ADDR = re.compile(r'\b(?:\d|[1-9]\d|1\d\d|2[0-5]{2})\.(?:\d|[1-9]\d|1\d\d|2[0-5]{2})\.(?:\d|[1-9]\d|1\d\d|2[0-5]{2})\.(?:\d|[1-9]\d|1\d\d|2[0-5]{2})(?:/[1-9]|/1[0-9]|/2[0-4])?\b')
IPV4_ADDR_2 = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:/[1-9]|/1[0-9]|/2[0-4])?$')
