#!/usr/bin/env python3

# Liam Nolan (c) 2019 ISC
# Full licence terms located in LICENCE file

from logging import getLogger, StreamHandler, Formatter
from logging.handlers import WatchedFileHandler, SysLogHandler
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

from blacklistparser.core import types


class StartLog:
    def __init__(self, verbose=False, quiet=False, syslog=None, logpath=None, loglevel=None):
        '''
        start logging facilities
        pass an optional logpath to log to disk (using WatchedFileHandler)
        '''
        levels = {'DEBUG':DEBUG, 'INFO':INFO, 'WARNING':WARNING, 'ERROR':ERROR, 'CRITICAL':CRITICAL}
        assert loglevel in levels.keys() or loglevel == None, 'log level must be one of ' + str(levels)
        # set loglevel based on verbosity/quiet args
        if loglevel is not None:
            loglevel = levels[loglevel]
        elif verbose is True and quiet is False:
            loglevel = DEBUG
        elif quiet is True and verbose is False:
            loglevel = CRITICAL
        else:
            loglevel = INFO
        # logger
        formatter = Formatter('%(name)s - %(message)s')
        self.log = getLogger('blacklistparser')
        self.log.setLevel(loglevel)
        # setup console logger
        self.console_log = StreamHandler()
        self.console_log.setFormatter(formatter)
        self.console_log.setLevel(loglevel)
        self.log.addHandler(self.console_log)
        self.log.debug('Added StreamHandler() console logging')
        # alternative logging types below
        if logpath is None:
            self.log.debug('log path not specified')
        elif types.base_path_type(logpath) is not None:
            # setup disk log
            self.disk_log = WatchedFileHandler(logpath)
            self.disk_log.setFormatter(formatter)
            self.disk_log.setLevel(loglevel)
            self.log.addHandler(self.disk_log)
            self.log.debug('Added WatchedFileHandler() logging')
        if syslog:
            # setup syslog
            # this is using /dev/log socket that is very (linux/openbsd)
            # platform dependant, should add some os detection logic here
            # and an argument to log to remote syslog server/port
            self.sys_log_handler = SysLogHandler(address='/dev/log')
            self.sys_log_handler.setFormatter(formatter)
            self.sys_log_handler.setLevel(loglevel)
            self.log.addHandler(self.sys_log_handler)
            self.log.debug('Added SysLogHandler() logging')
        # log setup success/fail msg at DEBUG level
        debugmsg = ('setting log level to ' + str(loglevel))
        self.log.debug(debugmsg)
