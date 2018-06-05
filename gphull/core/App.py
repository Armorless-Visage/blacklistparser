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


class App:
    def __init__(self):
        '''
        setup base class for pybl applications
        '''
        self.setup_logging(
                self.args.logpath,
                self.args.verbose,
                self.args.quiet,
                self.args.syslog)
        self.setup_args()
        self.db = Database.Manager(self.args.database)

    def setup_args(self):        
        '''
        argparse
        '''
        self.parent_parser = ArgumentParser(
            prog='gphull',
            conflict_handler='resolve',
            add_help=False)
        self.subparser = self.parent_parser.add_subparsers(dest=subparser_name)
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
            type=FileType('wb', 0),
            action='store'
            )
    
        '''
        source subparser
        '''
        self.source_parser = self.subparser.add_parser('source')
        self.source_parser.set_defaults(func=action_source)
        self.add_ex = self.source_parser.add_mututally_exclusive_group(required=True)
        self.add_ex.add_argument(
            '-a',
            '--add',
            help='Add a source url eg. http://example.com/blacklist',
            action='store',
            )
        self.source_parser.add_argument(
            '-f',
            '--frequency',
            help='Frequency in seconds to update from source url',
            action='store',
            type=types.frequency_range,
            )
        
        self.add_ex.add_argument(
            '-r',
            '--remove',
            help='Remove a source url.',
            action='store',
            )
        self.source_parser.add_argument(
            '-f',
            '--format',
            help='input/output format',
            type=types.format_type,
            action='store'
            )
        '''
        output subparser
        '''
        self.output_parser = self.subparser.add_parser('output')
        self.output_parser.set_defaults(func=action_output)
        self.out_ex = self.output_parser.add_mututally_exclusive_group(required=True)
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
        
    def setup_logging(self, log_path=None, verbose=False, quiet=False, use_syslog=False):
        '''
        start logging facilities
        pass an optional log_path to log to disk (using WatchedFileHandler)
        '''
        #levels = (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        # set loglevel based on verbosity/quiet args
        if verbose is True and quiet is False:
            loglevel = DEBUG
        elif quiet is True and verbose is False:
            loglevel = CRITICAL
        else:
            loglevel = INFO
        # logger
        formatter = Formatter('%(asctime)s - %(name)s - %(message)s')
        self.log = getLogger('gphull')
        self.log.setLevel(loglevel)
        # setup console logger
        self.console_log = StreamHandler()
        self.console_log.setFormatter(formatter)
        self.console_log.setLevel(loglevel)
        self.log.addHandler(self.console_log)
        self.log.debug('Added StreamHandler() console logging')
        # alternative logging types below
        if log_path is None:
            '''
            do nothing as disk logging is not requested
            TODO: check permissions and try to fix
            '''
            self.log.debug('log path not specified')
        elif types.base_path_type(log_path) is not None:
            # setup disk log
            self.disk_log = WatchedFileHandler(log_path)
            self.disk_log.setFormatter(formatter)
            self.disk_log.setLevel(loglevel)
            self.log.addHandler(self.disk_log)
            self.log.debug('Added WatchedFileHandler() logging')
        if use_syslog is True:
            # setup syslog
            # this is using /dev/log socket that is very (linux/openbsd)
            # platform dependant, should add some os detection logic here
            # and an argument to log to remote syslog server/port
            self.sys_log = SysLogHandler(address='/dev/log')
            self.sys_log.setFormatter(formatter)
            self.sys_log.setLevel(loglevel)
            self.log.addHandler(self.sys_log)
            self.log.debug('Added SysLogHandler() logging')
        # log setup success/fail msg at DEBUG level
        debugmsg = ('setting log level to ' + str(loglevel))
        self.log.debug(debugmsg)
    
    def action_source(self):
        if self.args.add is not None:
            # attempt to add a url
            Database.Utilities.add_source_url(
                self.db,
                self.args.add,
                self.args.format,
                self.args.frequency)
            self.db.db_conn.commit()
    
        # remove a url
        elif self.args.remove is not None:
            # attempt to remove url 
            Database.Utilities.delete_source_url(
                self.db,
                self.args.remove)
            self.db.db_conn.commit()
        else:
            raise self.source_parser.error()
    
    def action_adddress(self):
        if self.args.add is not None:
            Database.Utilities.add_element(
                    self.db,
                    self.args.address,
                    self.args.format,
                    self.source_url)
        elif self.args.remove is not None:
            raise self.source_parser.error('TODO implement this!!!')
        else:
            raise self.source_parser.error()
    
    def action_output(self):
        if self.args.format is None:
            raise self.source_parser.error('Must specify a output --format')
        if self.args.output is None:
            raise self.source_parser.error('Must specify a output --file')
#        output_list = Database.Utilities.pull_names(    
