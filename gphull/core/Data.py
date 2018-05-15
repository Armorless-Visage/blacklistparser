#!/usr/bin/env python3
# Liam Nolan (c) 2018 ISC

from gphull.core import Parser, Exceptions, Database
from abc import abstractmethod, ABCMeta

class Content(metaclass=ABCMeta):
    def __init__(self, input_data, source_url):
        
        self.input_data = input_data
        self.datatype = Parser.format_detector(self.input_data)
        self.parser = Parser.types[self.datatype](self.input_data)
        self.content = parser(self.input_data)
        self.source_url = source_url

        @abstractmethod
        def add_to_db(self, db_manager):
            pass

class DataList(Content):
    def __init__(self):
        # for iter
        self.index = len(self.content)
        
        # check args
        if self.datatype not in Parser.types.keys():
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
        if Database.Utilities.bulk_add(
                db_manager,
                self.content,
                self.datatype,
                self.source_url) is True:
            pass
        else:
            errmsg = 'Error adding list to database'
            raise Exceptions.ExtractorError(errmsg)


class DataElement(Content):
    def __init__(self, data, datatype, source_url):
        # check args
        if self.input_data is not str:
            raise TypeError('data must be a string')
        if self.datatype not in Parser.types.keys():
            errmsg = 'data type' + str(self.datatype) + 'not supported'
            raise Exceptions.IncorrectDataType(errmsg)
        if self.source_url is not str:
            raise TypeError('source_url must be a string)')

    def add_to_db(self, db_manager):
        '''
        add this list to a databaseb via db connection
        '''
        if Database.Utilities.add_element(
                db_manager,
                self.content,
                self.datatype,
                self.source_url) is True:
            pass
        else:
            errmsg = 'Error adding list to database'
            raise Exceptions.ExtractorError(errmsg)
