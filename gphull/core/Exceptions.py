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
class NoMatchesFound(ExtractorError):
    '''
    No matches found inside data
    '''
class IncorrectDataType(ExtractorError):
    '''
    Data type is not supported
    '''
class BadFileType(ExtractorError):
    '''
    File is of incorrect type
    '''
class EmptyList(ExtractorError):
    '''
    List contains no items
    '''
class NetError(ExtractorError):
    '''
    network error
    '''
class DatabaseError(ExtractorError):
    '''
    Error with database
    '''
class ValidatorError(ExtractorError):
    '''
    Error validating ip/domain
    '''
