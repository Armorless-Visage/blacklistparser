#!/usr/bin/env python3
# Liam Nolan (c) 2018 ISC

from blockparser.core import Parser, Exceptions

class DataList:
    def __init__(self, input_data):
        '''
        A iterable list of domains or ip addresses.
        '''
        self.input_data = input_data
        # autodetect format
        self.datatype = Parser.format_detector(self.input_data)
        # select parser based on format
        parser = Parser.extractor[self.datatype]
        # parser output is the list of domains/ips
        self.content = parser(self.input_data)
        # for iter
        self.index = len(self.content)
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.content[self.index]
