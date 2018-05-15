#!/usr/bin/env python3
# Liam Nolan (c) 2018 ISC

import re

'''
base regex patterns for matching domains modified from
Regular Expressions Cookbook
2nd Edition by Steven Levithan, Jan Goyvaerts
\b((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,63}\b
'''

domain_regex = r'\b((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,63}\b'
abp_domain = r'^(?:\|\|)(((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,63})(?:\^(\$third-party)?)$'
abp_domain_nothird = r'^(?:\|\|)(((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,63})(?:\^)$'
abp_version = r'^\[Adblock Plus 2\.0\]$'
newline_domain = r'^(((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,63})$'
ipv4_addr = '\b(?:\d|[1-9]\d|1\d\d|2[0-5]{2})\.(?:\d|[1-9]\d|1\d\d|2[0-5]{2})\.(?:\d|[1-9]\d|1\d\d|2[0-5]{2})\.(?:\d|[1-9]\d|1\d\d|2[0-5]{2})(?:/[1-9]|/1[0-9]|/2[0-4])?\b'
