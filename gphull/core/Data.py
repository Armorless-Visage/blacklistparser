#!/usr/bin/env python3
# Liam Nolan (c) 2018 ISC

import re
from io import StringIO
from abc import abstractmethod, ABCMeta
from gphull.core import Parser, Exceptions, Database, Regex

class Content(metaclass=ABCMeta):
    def __init__(self, data, source_url, datatype, db):

        self.data = data
        self.datatype = datatype
        self.source_url = source_url

        # check args
        if self.source_url is not str and self.source_url is not None:
            raise TypeError('source_url must be a string or None)')
        if self.datatype not in Parser.VALIDATOR.keys():
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

class DataElement(Content):
    def __init__(self):
        super()
        # check args
        if self.data is not str:
            raise TypeError('data must be a string')
        if self.datatype not in Parser.VALIDATOR.keys():
            errmsg = 'data type' + str(self.datatype) + 'not supported'
            raise Exceptions.IncorrectDataType(errmsg)
        if self.source_url is not str:
            raise TypeError('source_url must be a string)')
        if not Validator.VALIDATOR[self.datatype](self.data):
            raise Exceptions.ValidatorError('address not valid')

    def add_to_db(self, db_manager):
        '''
        add this list to a databaseb via db connection
        '''
        if Database.Manager.add_element(
                db_manager,
                self.data,
                self.datatype,
                self.source_url) is True:
            pass
        else:
            errmsg = 'Error adding list to database'
            raise Exceptions.ExtractorError(errmsg)

class Format:
    @staticmethod
    def newline(data):
        # return a StringIO file with one address per line
        # easy no boiler to add
        with StringIO() as mfile:
            for each in self.data:
                # validate before add (silent drops invalid)
                if VALIDATOR['newline'](each):
                    mfile.write(each)
        return mfile
    @staticmethod
    def ipset(data):
        # return a StringIO file with one address per line
        # easy no boiler to add
        with StringIO() as mfile:
            for each in self.data:
                # validate before add (silent drops invalid)
                if VALIDATOR['ipset'](each):
                    mfile.write(each)
        return mfile

class Validator:
    @staticmethod
    def ipv4_addr(addr):
        if Regex.IPV4_ADDR_ONLY.match(addr):
            return addr
        return None
    @staticmethod
    def domain(name):
        if Regex.NEWLINE_DOMAIN.match(addr):
            return addr
        return None

VALIDATOR = {
    'ipset' : Validator.ipv4_addr,
    'newline' : Validator.domain,
    'adblock' : Validator.domain }
FORMAT = {
        'ipset' : Format.ipset,
        'newline' : Format.newline }

            
