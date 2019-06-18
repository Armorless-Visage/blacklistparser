#!/usr/bin/env python3
# Liam Nolan (c) 2019 ISC

import re
from abc import ABCMeta, abstractmethod
from blacklistparser.core import Exceptions, Regex

class BaseParser(metaclass=ABCMeta):

    def __init__(self, data):
        self.origin_data = data
        self.results = self.extract_data(self.origin_data)

    @abstractmethod
    @staticmethod
    def extract_data(data):
        pass

    @classmethod
    def type_helper(cls, data):
        try:
            cls.extract_data(data)
        except Exceptions.NoMatchesFound:
            return None
        return data

class ABPParser(BaseParser):
    @staticmethod
    def extract_data(data):
        '''
        use re.finall to get domains out of ABP filters and return as a list of
        tuples containing regex groups
        returns the list or raises Exceptions.NoMatchesFound

        matches AdblockPlus (ABP) filter syntax for domain names
        eg. ||google.com^
        eg. ||google.com^$third-party
        '''
        # regex string for ABP domains in Regex.abp_domain
        pattern = re.compile(Regex.ABP_DOMAIN, re.MULTILINE)

        # exclude third party rules
        #   if third_party is not True:
        #       pattern = re.compile(Regex.abp_domain_nothird, re.MULTILINE)

        matches = re.findall(pattern, data)
        if matches:
            '''
            match objects come in a tuple for each regex group so the group
            containing the domain name must be separated
            '''
            index = len(matches)
            while index > 0:
                index = index - 1
                matches[index] = matches[index][0]
            return matches
        else:
            raise Exceptions.NoMatchesFound("No ABP syntax domains found.")

class NewlineParser(BaseParser):
    @staticmethod
    def extract_data(data):
        '''
        Extract newline data into a list
        eg.
        google.com
        wikipedia.org
        '''
        pattern = re.compile(Regex.NEWLINE_DOMAIN, re.MULTILINE)
        matches = re.findall(pattern, data)
        if matches:
            return matches
        else:
            raise Exceptions.NoMatchesFound("No newline formatted domains found.")

class IpsetParser(BaseParser):
    @staticmethod
    def extract_data(data):
        pattern = re.compile(Regex.IPV4_ADDR, re.MULTILINE)
        matches = re.findall(pattern, data)

        if matches:
            return matches
        else:
            raise Exceptions.NoMatchesFound("No ip addreses found.")

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
        ABPParser.extract_data(data)
        return 'adblock'
    except Exceptions.NoMatchesFound:
        pass
    # test newline format
    try:
        NewlineParser.extract_data(data)
        return 'newline'
    except Exceptions.NoMatchesFound:
        pass

    raise Exceptions.IncorrectDataType('Unable to detect format of input data.')

SHORTNAME = {'adblock' : ABPParser, 'newline' : NewlineParser, 'ipset' : IpsetParser}
