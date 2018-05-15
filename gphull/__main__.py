#!/usr/bin/env python3

# Liam Nolan (c) 2017
# BSD 2-Clause
# Full licence terms located in LICENCE file

from argparse import ArgumentParser
from argparse import ArgumentError
from logging import getLogger, StreamHandler, Formatter
from logging.handlers import WatchedFileHandler, SysLogHandler
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from gphull.core import Database, types


class App:
    def __init__(self):
        '''
        setup base class for pybl applications
        '''
        
        '''
        argparse
        '''
        self.parent_parser = ArgumentParser(prog='gphull', conflict_handler='resolve', add_help=False)

        self.parent_parser.add_argument(
                'action',
                help='''source: add or remove a source url
                address: add or remove an address
                update: updating database from source urls
                output: generate blacklists from database''',
                action='store',
                type=str,
                choices=['source', 'address', 'update', 'output']
                )

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

        # setup optional and positionally dependant args

        self.parent_parser.add_argument(
            '-f',
            '--format',
            help='input/output format',
            type=types.format_type,
            action='store'
            )
        self.parent_parser.add_argument(
            '-o',
            '--output',
            help='write to a file specified by this argument',
            type=types.base_path_type,
            action='store',
            )
        self.parent_parser.add_argument(
            '-e',
            '--timeout',
            help='n seconds before url or data expires',
            action='store',
            )

        self.add_remove = self.parent_parser.add_mutually_exclusive_group()

        self.add_remove.add_argument(
            '-a',
            '--add',
            help='Add an address. Either plain ip, cidr or a domain name',
            action='store',
            )
        
        self.add_remove.add_argument(
            '-r',
            '--remove',
            help='Remove an address. Either plain ip, cidr or a domain name',
            action='store',
            )

        self.parent_parser.add_argument(
            '-d',
            '--database',
            help='file path of database',
            type=types.base_path_type,
            action='store'
            )

        self.args = self.parent_parser.parse_args()
        
        self.setup_logging(
                self.args.logpath,
                self.args.verbose,
                self.args.quiet,
                self.args.syslog)

        # check for database arg
        if self.args.database is None:
            raise ArgumentError('must specify a --database')
        
        self.db = Database.Manager(self.args.database)

        if self.args.action == 'source':
            # check arguments
            if (self.args.add is None
                and self.args.remove is None
                and self.args.timeout is None):
                s_usg = ('<source> usage: source --format "ipset" ' +
                    '--timeout 3600 --add "https://example.com/blacklist"')
                raise ArgumentError(s_usg)
            if self.args.add is not None and self.args.timeout is None:
                raise ArgumentError('--timeout <s> must be specified')
            if self.args.add is not None:
                Database.Utilities.add_source_url(
                        self.db,
                        self.args.add,
                        self.args.format,
                        self.args.timeout)
                self.db.commit()
                
        if self.args.action == 'addresss':
            if self.args.timeout is not None:
                raise ArgumentError('--timeout can\'t be applied to an address')

        if self.args.action == 'update':
            if (self.args.timeout is not None
            or self.args.add is not None
            or self.args.remove is not None
            or self.args.format is not None):
                u_usg = '<update> usage: update --database /path/to/db.sqlite'
                raise ArgumentError(u_usg)

        if self.args.action == 'output':
            if (self.args.output is None
            or self.args.format is None):
                o_usg = ('<output> usage: output -d /path/to/db.sqlite3 '
                        + '-f ipset -o /path/to/blacklist.ipset')
                raise(AgumentError('o_usg'))


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

if __name__ == '__main__':
    try:
        App()
    except KeyboardInterrupt:
        raise
