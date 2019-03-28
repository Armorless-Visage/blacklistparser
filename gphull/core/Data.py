#!/usr/bin/env python3
# Liam Nolan (c) 2018 ISC

from abc import abstractmethod, ABCMeta
from gphull.core import Exceptions, Database, Regex


class IPList:
    def __init__(self, data, raise_errors=False, source=None):
        self.data = []
        self.datatype = 'ipset'
        self.index = -1 # start index at -1 b/c it is inc before return
        self.source_url = source
        for line in data:
            stringified = str(line)
            if not VALIDATOR[self.datatype](stringified, printerr=False):
                # if raise_errors is true throw an exception
                if raise_errors:
                    errmsg = ("Not a valid " + self.datatype + " address")
                    raise Exceptions.ValidatorError(errmsg)
            else:
                self.data.append(stringified)
            
    def __iter__(self):
        return self
    def __next__(self):
        if self.index > len(self.data):
            raise StopIteration 
        self.index += 1
        return self.data[self.index]
    
    def add_to_db(self, db_manager):
        '''
        add this list to a databaseb via db connection
        '''
        # re-validate before entering into db
        if Database.Manager.bulk_add(
                db_manager,
                self.data,
                'ip',
                self.source_url) is True:
            pass
        else:
            errmsg = 'Error adding list to database'
            raise Exceptions.ExtractorError(errmsg)

class Content(metaclass=ABCMeta):
    def __init__(self, data, source_url, datatype, db):

        self.data = data
        self.datatype = datatype
        self.source_url = source_url

        # check args
        if self.source_url is not str and self.source_url is not None:
            raise TypeError('source_url must be a string or None)')
        if self.datatype not in VALIDATOR.keys():
            errmsg = 'data type' + str(self.datatype) + 'not supported'
            raise Exceptions.IncorrectDataType(errmsg)
        
        @abstractmethod
        def add_to_db(self, db_manager):
            pass

class DataList(Content):
    def __init__(self):
        super()
        # for iter
        self.index = len(self.data)
        
        for each in self.data:
            if not VALIDATOR[self.datatype](each):
                errmsg = ("Not a valid " + self.datatype + " address")
                raise Exceptions.ValidatorError(errmsg)

    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.data[self.index]

    def add_to_db(self, db_manager):
        '''
        add this list to a databaseb via db connection
        '''
        if not VALIDATOR[self.datatype](self.data):
            errmsg = ('address not type ' + self.datatype)
            raise Exceptions.IncorrectDataType(errmsg)
        if Database.Manager.bulk_add(
                db_manager,
                self.data,
                self.datatype,
                self.source_url) is True:
            pass
        else:
            errmsg = 'Error adding list to database'
            raise Exceptions.ExtractorError(errmsg)
        return True

class Format:
    '''
    produce lists of data to write to a file, inserts
    formatting and header footers as required by the format
    NOTE: Validate elsewhere
    '''
    @staticmethod
    def newline(data):
        '''
        easy just return the data with newlines no formatting required
        '''
        sep = '\n'
        output = sep.join(data)
        return output

class Validator:
    @staticmethod
    def ipv4_addr(addr, printerr=False):
        if Regex.IPV4_ADDR_2.match(addr):
            return addr
        else:
            if printerr:
                print(addr)
        return None
    @staticmethod
    def domain(name):
        if Regex.NEWLINE_DOMAIN.match(name):
            return name
        return None

VALIDATOR = {
    'ipset' : Validator.ipv4_addr,
    'newline' : Validator.domain,
    'adblock' : Validator.domain }
FORMAT = {
        'ipset' : Format.newline,
        'newline' : Format.newline }

            
