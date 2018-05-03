#!/usr/bin/env python3
# Liam Nolan (c) 2018 ISC

import re
from blockparser.core import Exceptions, Regex

def find_abp_data(inputstr):
    '''
    use re.finall to get domains out of ABP filters and return as a list of
    tuples containing regex groups
    returns the list or raises Exceptions.NoMatchesFound
    '''
    '''
    matches AdblockPlus (ABP) filter syntax for domain names
    eg. ||google.com^
    eg. ||google.com^$third-party
    '''
    
    # regex string for ABP domains in Regex.abp_domain
    pattern = re.compile(Regex.abp_domain, re.MULTILINE)

    # exclude third party rules
#   if third_party is not True:
#       pattern = re.compile(Regex.abp_domain_nothird, re.MULTILINE)
    
    matches = re.findall(pattern, inputstr)
    if len(matches) != 0:
        '''
        match objects come in a tuple for each regex group so the group
        containing the domain name must be isolated
        '''
        index = len(matches)
        while index > 0:
            index = index - 1
            matches[index] = matches[index][0]
        return matches
    else:
        raise Exceptions.NoMatchesFound("No ABP syntax domains found.")

def find_newline_data(data):
    '''
    Extract newline data into a list
    eg.
    google.com
    wikipedia.org
    '''
    pattern = re.compile(Regex.newline_domain)
    matches = re.matchall(Regex.newline_domain)
    if len(matches) != 0:
        return matches

    else:
        raise Exceptions.NoMatchesFound("No newline formatted domains found.")

def format_detector(data):
    '''
    Automatic detection of data type. Returns either a string naming the content
    type or raises a BadDataType exception
    Currently supported types and return values are below.
    supported, return_value
        - adblock plus filter format, 'adblock'
        - domain per line, 'newline'
    '''
    # test adblock plus filter format
    try:
        find_abp_data(data)    
        return 'adblock'       
    except Exceptions.NoMatchesFound:
        pass
    # test newline format
    try:
        find_newline_data(data)
        return 'newline'       
    except Exceptions.NoMatchesFound:
        pass

    raise Exceptions.IncorrectDataType('Unable to detect format of input data.')

extractor = { 'adblock' : find_abp_data, 'newline' : find_newline_data }
