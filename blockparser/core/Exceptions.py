#!/usr/bin/env python3
# Liam Nolan 2018 (c) ISC

class ExtractorError(Exception):
    '''
    Base exception class
    '''
    pass

class NotString(ExtractorError):
    '''
    Value is not a string
    '''
    pass
class NotMatch(ExtractorError):
    '''
    String does not match regex patten
    '''
    pass
class NoMatchesFound(ExtractorError):
    '''
    No matches found inside data
    '''
class NoDomainsFound(ExtractorError):
    '''
    No domains found inside data
    '''
class IncorrectDataType(ExtractorError):
    '''
    No domains found inside data
    '''

