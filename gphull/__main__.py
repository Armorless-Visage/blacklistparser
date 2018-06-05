#!/usr/bin/env python3

# Liam Nolan (c) 2017
# BSD 2-Clause
# Full licence terms located in LICENCE file

from argparse import ArgumentParser
from argparse import ArgumentError
from logging import getLogger, StreamHandler, Formatter
from logging.handlers import WatchedFileHandler, SysLogHandler
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from gphull.core import types, Exceptions, net, Parser, Data
from gphull.core import Database


class App:
    def __init__(self):
        '''
        setup base class for pybl applications
        '''
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
