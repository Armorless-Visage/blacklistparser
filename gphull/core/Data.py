#!/usr/bin/env python3
# Liam Nolan (c) 2018 ISC

import re
from abc import abstractmethod, ABCMeta
from gphull.core import Parser, Exceptions, Database, Regex

class Content(metaclass=ABCMeta):
    def __init__(self, data, source_url, datatype):

        self.data = data
        self.datatype = datatype
        self.source_url = source_url

        @abstractmethod
        def add_to_db(self, db_manager):
            pass

class DataList(Content):
    def __init__(self):
        super()
        # for iter
        self.index = len(self.content)
        
        # check args
        if self.datatype not in Parser.SHORTNAME.keys():
            errmsg = 'data type' + str(self.datatype) + 'not supported'
            raise Exceptions.IncorrectDataType(errmsg)
        if self.source_url is not str:
            raise TypeError('source_url must be a string)')

    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.content[self.index]

    def add_to_db(self, db_manager):
        '''
        add this list to a databaseb via db connection
        '''
        if Database.Manager.bulk_add(
                db_manager,
                self.content,
                self.datatype,
                self.source_url) is True:
            pass
        else:
            errmsg = 'Error adding list to database'
            raise Exceptions.ExtractorError(errmsg)


class DataElement(Content):
    def __init__(self):
        super()
        # check args
        if self.input_data is not str:
            raise TypeError('data must be a string')
        if self.datatype not in Parser.SHORTNAME.keys():
            errmsg = 'data type' + str(self.datatype) + 'not supported'
            raise Exceptions.IncorrectDataType(errmsg)
        if self.source_url is not str:
            raise TypeError('source_url must be a string)')
        if not Validator.SHORTNAME[self.datatype](self.content):
            raise Exceptions
            

    def add_to_db(self, db_manager):
        '''
        add this list to a databaseb via db connection
        '''
        if Database.Manager.add_element(
                db_manager,
                self.content,
                self.datatype,
                self.source_url) is True:
            pass
        else:
            errmsg = 'Error adding list to database'
            raise Exceptions.ExtractorError(errmsg)

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
SHORTNAME = {
    'ipset' : Validator.ipv4_addr,
    'newline': Validator.domain,
    'adblock': Validator.domain }

            
