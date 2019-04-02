#!/usr/bin/env python3
# Liam Nolan (c) 2018 ISC

from gphull.core import Exceptions, Database, Regex


class DataList:
    def __init__(self, data, datatype, source=None, raise_errors=False):
        self.data = []
        self.index = -1 # start index at -1 b/c it is inc before return
        self.source_url = source

        if datatype not in VALIDATOR.keys():
            errmsg = 'data type ' + str(datatype) + ' not supported'
            raise Exceptions.IncorrectDataType(errmsg)
        self.datatype = datatype
        self.base_type = BASE_TYPE[self.datatype]

        for line in data:
            stringified = str(line)
            if not VALIDATOR[self.datatype](stringified):
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
                self.base_type,
                self.source_url) is True:
            pass
        else:
            errmsg = 'Error adding list to database'
            raise Exceptions.ExtractorError(errmsg)

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

    @staticmethod
    def unbound_nxdomain(data):
        '''
        for use with unbound
        # TODO use generator to fix memory problems
        '''
        sep = '" always_nxdomain\nlocal-zone: "'
        output = sep.join(data)
        output = 'local-zone: "' + output + '" always_nxdomain'
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
    'domain' : Validator.domain,
    'ip' : Validator.ipv4_addr,
    'adblock' : Validator.domain}
BASE_TYPE = {
    'ipset' : 'ip',
    'ip' : 'ip',
    'domain' : 'domain',
    'adblock' : 'domain',
    'unbound_nxdomain' : 'domain'}
FORMAT = {
        'ipset' : Format.newline,
        'unbound_nxdomain' : Format.unbound_nxdomain }


