#!/usr/bin/env python3

# Liam Nolan (c) 2017
# BSD 2-Clause
# Full licence terms located in LICENCE file

from argparse import ArgumentParser
from argparse import ArgumentError
from argparse import FileType
from logging import getLogger, StreamHandler, Formatter
from logging.handlers import WatchedFileHandler, SysLogHandler
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from gphull.core import Database, types, Exceptions, net, Parser, Data
from gphull.core import Logging


class App:
    def __init__(self):
        '''
        setup base class for pybl applications
        '''
        self.setup_args()
        self.logger = Logging.StartLog(
            self.args.verbose,
            self.args.quiet,
            self.args.syslog,
            self.args.logpath)
        self.logger.log.info('initalizing database')
        self.db = Database.Manager(self.args.database)
        self.parser_action = { 
            'source': self.action_source,
            'address': self.action_adddress,
            'update': self.action_update,
            'output': self.action_output }
        self.parser_action[self.args.subparser_name]()

    def setup_args(self):        
        '''
        argparse
        '''
        self.parent_parser = ArgumentParser(
            prog='gphull',
            conflict_handler='resolve',
            add_help=False)
        self.subparser = self.parent_parser.add_subparsers(dest='subparser_name')
        self.source_parser = self.subparser.add_parser('source')
        self.address_parser = self.subparser.add_parser('address')
        self.update_parser = self.subparser.add_parser('update')
        self.output_parser = self.subparser.add_parser('output')
    
        # add option to control logging output level
        self.logging = self.parent_parser.add_argument_group()
        self.logging_verb = self.parent_parser.add_mutually_exclusive_group()
        self.logging_verb.add_argument(
            '-v',
            '--verbose',
            help='make the programs output more verbose',
            action='store_true'
            )
        self.logging_verb.add_argument(
            '-q',
            '--quiet',
            help='quiet the programs output',
            action='store_true'
            )
        self.logging_verb.add_argument(
            '-l',
            '--loglevel',
            help='specify a loglevel by number 0-7',
            type=int,
            choices=[0, 1, 2, 3, 4, 5, 6, 7],
            action='store'
            )
    
    
        self.logging.add_argument(
            '-l',
            '--logpath',
            help='write log output to a file specified by this argument',
            type=types.base_path_type,
            action='store',
            )
        self.logging.add_argument(
            '-s',
            '--syslog',
            help='use user syslog facility for logging',
            action='store_true',
            default=True)
    
        self.parent_parser.add_argument(
            '-d',
            '--database',
            help='file path of database',
            type=types.base_path_type,
            action='store',
            required=True
            )
    
        '''
        source subparser
        '''
        self.source_parser = self.subparser.add_parser('source')
        self.source_parser.set_defaults(func=self.action_source)
        self.add_ex = self.source_parser.add_mutually_exclusive_group(required=True)
        self.add_ex.add_argument(
            '-a',
            '--add',
            help='Add a source url eg. http://example.com/blacklist',
            action='store',
            )
        self.source_parser.add_argument(
            '-f',
            '--frequency',
            help='Frequency in seconds between updating source urls',
            action='store',
            type=int,
            required=True
            )
        
        self.add_ex.add_argument(
            '-r',
            '--remove',
            help='Remove a source url.',
            action='store',
            )
        self.source_parser.add_argument(
            '-t',
            '--type',
            help='input/output format',
            type=types.format_type,
            action='store'
            )
        '''
        output subparser
        '''
        self.output_parser = self.subparser.add_parser('output')
        self.output_parser.set_defaults(func=self.action_output)
        self.out_ex = self.output_parser.add_mutually_exclusive_group(required=True)
        self.output_parser.add_argument(
            '-f',
            '--format',
            help='input/output format',
            type=types.format_type,
            action='store'
            )
        self.output_parser.add_argument(
            '-o',
            '--output',
            help='write to a file specified by this argument',
            type=types.base_path_type,
            action='store',
            )
    
        self.args = self.parent_parser.parse_args()
        return self.args
        
    def action_source(self):
        self.logger.log.debug('starting source action')
        if self.args.add is not None:
            # attempt to add a url
            logmsg = ('attempting to add source url: ' + self.args.add)
            self.logger.log.info(logmsg)
            Database.Manager.add_source_url(
                self.db,
                self.args.add,
                self.args.type,
                self.args.frequency)
            self.db.db_conn.commit()
            # check url is added
            if (Database.Manager.test_source_url(
                self.db,
                self.args.add) is True):
                self.logger.log.info('added source url to database OK')
                exit(0)
            else:
                self.logger.log.error('FAILED to add source url to database')
                exit(1)

        # remove a url
        elif self.args.remove is not None:
            # attempt to remove url 
            Database.Manager.delete_source_url(
                self.db,
                self.args.remove)
            self.db.db_conn.commit()
        else:
            raise self.source_parser.error()
    
    def action_adddress(self):
        if self.args.add is not None:
            Database.Manager.add_element(
                    self.db,
                    self.args.address,
                    self.args.format,
                    self.args.source_url)
        elif self.args.remove is not None:
            raise self.source_parser.error('TODO implement this!!!')
        else:
            raise self.source_parser.error()
    
    def action_output(self):
        if self.args.format is None:
            raise self.source_parser.error('Must specify a output --format')
        if self.args.output is None:
            raise self.source_parser.error('Must specify a output --file')
#        output_list = Database.Manager.pull_names(
    def action_update(self):
        pass
