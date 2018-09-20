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
from tempfile import NamedTemporaryFile
from shutil import copyfile
from tempfile import mkstemp


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
            'address': self.action_address,
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
        self.subparser = self.parent_parser.add_subparsers(
            dest='subparser_name')
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
    
        '''
        source subparser
        '''
        self.source_parser.set_defaults(func=self.action_source)
        self.source_parser.add_argument(
            '-d',
            '--database',
            help='file path of database',
            type=types.base_path_type,
            action='store',
            required=True
            )
        self.source_ex = self.source_parser.add_mutually_exclusive_group(
            required=True)
        self.source_ex.add_argument(
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
        
        self.source_ex.add_argument(
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
            action='store',
            choices=list(Data.VALIDATOR)[0],
            required=True
            )
        '''
        address subparser
        '''
        self.address_parser.set_defaults(func=self.action_address)
        self.address_parser.add_argument(
            '-d',
            '--database',
            help='file path of database',
            type=types.base_path_type,
            action='store',
            required=True
            )
        self.address_ex = self.address_parser.add_mutually_exclusive_group(
            required=True)
        self.address_ex.add_argument(
            '-a',
            '--add',
            help='Add a source url eg. http://example.com/blacklist',
            action='store',
            )
        self.address_parser.add_argument(
            '-f',
            '--frequency',
            help='Frequency in seconds between updating source urls',
            action='store',
            type=int,
            required=True
            )
        
        self.address_ex.add_argument(
            '-r',
            '--remove',
            help='Remove a source url.',
            action='store',
            )
        self.address_parser.add_argument(
            '-t',
            '--type',
            help='input/output format',
            action='store',
            choices=['ip', 'domain'],
            required=True
            )
        self.address_parser.add_argument(
            '-s',
            '--source',
            help='define a url to be set as the source of the address',
            action='store',
            type=types.format_type
            )
        '''
        output subparser
        '''
        self.output_parser = self.subparser.add_parser('output')
        self.output_parser.set_defaults(func=self.action_output)
        self.output_parser.add_argument(
            '-d',
            '--database',
            help='file path of database',
            type=types.base_path_type,
            action='store',
            required=True
            )
        self.output_parser.add_argument(
            '-f',
            '--format',
            help='input/output format',
            type=types.format_type,
            action='store',
            required=True,
            )
        self.output_parser.add_argument(
            '-o',
            '--output',
            help='write to a file specified by this argument',
            type=types.base_path_type,
            action='store',
            required=True,
            )
        expiry_help = ('Specify an expiry in seconds. Blacklist entries older '
                + 'than this argument will not be included.')
        self.output_parser.add_argument(
            '-e',
            '--expiry',
            help=expiry_help,
            type=int,
            action='store',
            required=True
            )
    
        self.args = self.parent_parser.parse_args()
    
        self.args = self.parent_parser.parse_args()
        if self.args.subparser_name is None:
            no_action_msg = ('An action must be specified. eg. '
                + 'gphull --database /tmp/test.db source'
                + '--add https://example.com --frequency 3600 '
                + '--type \'ipset\'')
            raise self.parent_parser.error(no_action_msg)
        # so the function can be used to get the args directly, return the parsed args
        # FIXME lame hack
        ipf = ['ipset']
        dof = ['newline', 'adblock']
        if self.args.format in ipf:
            self.base_type = 'ip'
        elif self.args.format in dof:
            self.base_type = 'domain'
        else:
            raise Exceptions.IncorrectDataType('FIXME THIS SHOULDN\'t OCCUR')
        return self.args
        
    def action_source(self):
        self.logger.log.debug('starting source action')
        if self.args.add is not None:
            # attempt to add a url
            logmsg = ('attempting to add source url: ' + self.args.add)
            self.logger.log.info(logmsg)
            try:
                Database.Manager.test_source_url(
                self.db,
                self.args.add)
                self.logger.log.info('source url already present in database')
                # success
                exit(0)
            except Exceptions.NoMatchesFound:
                # excpected when adding a new url
                pass

            Database.Manager.add_source_url(
                self.db,
                self.args.add,
                self.args.type,
                self.args.frequency)
            # commit
            self.db.db_conn.commit()
            # check url is added
            try:
                Database.Manager.test_source_url(
                    self.db,
                    self.args.add)
                self.logger.log.info('source added to database OK')
                # success
                exit(0)
            except Exceptions.NoMatchesFound:
                self.logger.log.error('FAILED to add source url to database!')
                # fail
                exit(1)

        # remove a url
        elif self.args.remove is not None:
            # check url is actually in db
            try:
                self.db.test_source_url(self.args.remove)
            except Exceptions.NoMatchesFound:
                msg = 'Entry does not exist in the database.'
                self.logger.log.info(msg)
                exit(0)
            # attempt to remove url
            self.db.delete_source_url(self.args.remove)
            self.db.db_conn.commit()
            # check removal is ok
            try:
                self.db.test_source_url(self.args.remove)
                msg = 'FAILED removing source url from database!'
                self.logger.log.error(msg)
            except Exceptions.NoMatchesFound:
                # success removing url
                self.logger.log.info('Removed source url from database OK')
            
        else:
            msg = 'source action must include --add or --remove'
            raise self.source_parser.error(msg)
    
    def action_address(self):
        if self.args.add is not None:
            self.db.add_element(
                    self.args.add,
                    self.args.type,
                    self.args.source)
            self.db.db_conn.commit()
        elif self.args.remove is not None:
            self.db.remove_element(
                self.args.remove,
                self.args.source)
            self.db.db_conn.commit()
        else:
            sperr = 'either --add or --remove must be specified'
            raise self.source_parser.error(sperr)
    
    def action_output(self):
        err = 0 # invalid lines
        valid = 0 # valid lines
        pending = []
        results = self.db.pull_names_2(self.args.expiry, self.base_type)
        for result in results:
            if Data.VALIDATOR[self.args.format](result):
                valid += 1
                pending.append(result)        
            else:
                err += 1
        ## LOG
        icountmsg = ('Counted ' + str(err) + ' invalid addresses')
        # log how many addresses where dropped
        self.logger.log.info(icountmsg)
        countmsg = ('Counted ' + str(valid) + ' valid addresses')
        # log how many addresses are valid
        self.logger.log.info(countmsg)
      
        if len(pending) < 1:
            self.logger.log.error('No addresses found. Exiting.')
            exit(1)

        # format the page
        output = Data.FORMAT[self.datatype](pending)
 
        with mkstemp('w+b', prefix="blparser", suffix=".tmp") as tmpf:
            try:
                tmpf.write(output.read())
                copyfile(tmpf, self.args.output)
            except:
                self.logger.log.error('FAILED copying tmpfile to destination')
                raise
        exit(0)        
        
    def action_update(self):
        pass
