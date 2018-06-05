#!/usr/bin/env python
# Liam Nolan (c) 2018

from sys import stderr, exit
from os import urandom, path
from struct import unpack
from time import time
from gphull.core import Exceptions
import sqlite3

class Manager:
    def __init__(self, db_path=None):
        '''
        - opens a connection to a sqlite3 db (or creates a new one)
        - db_path is the pathname of the sqlite3 database
        '''
        if path.isfile(db_path):
            # check file is sqlite3 format
            if self.sqlite3_db_file_type(db_path) is False:
                errmsg = 'Existing file ' + str(db_path) + ' is not a sqlite3 database'
                raise Exceptions.BadFileType(errmsg)
            # check file has the right application_id for blocklistparser
            if self.sqlite3_db_application_id(db_path) is False:
                errmsg = 'File is a sqlite3 db, but the application_id is not correct'
                raise Exceptions.BadFileType(errmsg)
        try:
            self.db_conn = sqlite3.connect(db_path)
            self.db_cur = self.db_conn.cursor()
            self.init_db()
        except sqlite3.OperationalError or sqlite3.DatabaseError:
            # TODO insert exception handling here
            #      - permissions check, symlink, path
            raise


    def init_db(self):
        '''
        initalizes the database tables 'sources' to hold source urls
        and update frequency, and 'data' to hold the actual content in those pages
        '''
        # sources table gets special formatting
        source_table = ("CREATE TABLE IF NOT EXISTS sources ( " +
                "url TEXT UNIQUE, " +
                "page_format TEXT, " +
                "timeout REAL, " +
                "last_updated REAL )")
        data_table = ("CREATE TABLE IF NOT EXISTS data ( " +
                "name TEXT, " +
                "data_format TEXT, " + 
                "first_seen REAL, " +
                "last_seen REAL, " +
                "source_url TEXT, " +
                "UNIQUE ( name, source_url ))")
        groups_table = ("CREATE TABLE IF NOT EXISTS data ( " +
                "name TEXT, " + 
                "membership TEXT )")
        application_id = ("PRAGMA application_id = 1915402268")
        user_version = ("PRAGMA user_version = 0x1")
        try:
            self.db_cur.execute(application_id)
            self.db_cur.execute(user_version)

            self.db_cur.execute(source_table)
            self.db_cur.execute(data_table)
            self.db_cur.execute(groups_table)
            self.db_conn.commit()
            return True
        except sqlite3.DatabaseError:
            raise
        
    def pull_names(self):
        '''
        returns a list of tuples of elements name, rowid from the input table
        select arg is passed as where=? to sqlite3
        '''
        line = (" SELECT name, rowid FROM data ")
        cur = self.db_cur
        self.db_cur.execute(line)
        return cur.fetchall()
    
    def pull_names_within_timout(self, timeout):
        '''
        returns a list of tuples of elements name, rowid from the input table
        select arg is passed as where=? to sqlite3
        '''
        join = (timeout, time())
        line = (' SELECT name FROM data WHERE last_seen + ? >= ? ')
        cur = self.db_cur
        self.db_cur.execute(line)
        return cur.fetchall()
    def pull_names_2(self, timeout, group):
        join = (timeout, time())
        line = ('SELECT name from data WHERE (last_seen + ? >= ?) AND (group = ?)')
        
    
    def pull_active_source_urls(self):
        '''
        return a list of the blacklist urls that need updating from sources
        '''
        ctime = (time(),)
        cur = self.db_cur
        self.db_cur.execute('''SELECT url FROM sources WHERE ? >= last_updated + timeout''', ctime)
        # any invalid urls found increment this
        errcnt = 0
        urls = []
        for url_result in cur.fetchall():
            if url_result[0] is not None:
                urls.append(url_result[0])
            else:
                errcnt += 1
        if len(urls) > 0:
            return urls
        else:
            errmsg = ('All urls on cooldown or none in database. Invalid urls found in db: ' + str(errcnt))
            raise Exceptions.NoMatchesFound(errmsg)
        
    def bulk_add(self, data_lst, data_type, source_url):
        '''
        add a list of items to the db using executemany
        ! Does not validate do it elsewhere TODO integrate val here
        ! Does not explicitly commit
        '''
        cur = self.db_cur
        current_time = time()

        time_update = [] 
        data_insert = []
         
        # check there is something to add then format and add them all using executemany
        if not data_lst:
            errmsg = 'No items to add.'
            raise Exceptions.EmptyList(errmsg) 
        for each in data_lst:
            data = each.rstrip()
            data_insert.append((data, data_type, current_time, current_time, source_url))
            time_update.append((current_time, data, source_url))
        
        iline = (" INSERT OR IGNORE INTO data" +
                " VALUES ( ?, ?, ?, ?, ? )")
        self.db_cur.executemany(iline, data_insert)
        tline = (" UPDATE data" + 
                " SET last_seen=? WHERE name=? AND source_url=?")
        self.db_cur.executemany(tline, time_update)
        #NOTE: this code above only writes the last url w/ addr to source
        return True
    
    def add_element(self, data, data_type, source_url):
        '''
        add a single element to the db
        NOTE: this checks time.time() every time it is executed, probably
        going to be very slow if it's called lots
        '''
        cur = self.db_cur
        if type(data) is not str:
            raise Exceptions.NotString('address must be a string')
        element = data.rstrip()
        current_time = time()
        data_insert = ( element, data_type, current_time, current_time, source_url ) 
        time_update = ( current_time, source_url, element )
        
        line = (" INSERT OR IGNORE INTO data" +
                " VALUES ( ?, ?, ?, ?, ? ) ")
        time_line = (" UPDATE data" +
            " SET last_seen=?, source=? WHERE name=?")
        self.db_cur.execute(line, data_insert)
        self.db_cur.execute(time_line, time_update)
    
    def add_source_url(self, url, dataformat, timeout):
        '''
        - Add a blacklist source to the database, returns True for OK, False
          otherwise
        - url: source of blacklist eg. https://example.com/blacklist.txt
        - target: table is this url being used to update
        - source_format: tells decoding what type the page is, eg per line,
          csv, rar
        - timeout: seconds between updates
        '''
        # NOTE: Do sql real vals overflow after 64b?
    
        cur = self.db_cur
        # url, source page format, page update timeout,
        # last_updated set to 61sec after epoch (never)
        t = ( str(url), str(dataformat), float(timeout), float(61) )
        
        try:
            self.db_cur.execute('''INSERT OR IGNORE INTO sources VALUES ( ?, ?, ?, ? )''', t)
        except sqlite3.DatabaseError:
            raise
        return True

    def delete_source_url(self, url):
        '''
        delete a blacklist source url from the database
        '''
        cur = self.db_cur
        url_tuple = ( str(url), )
        try:
            self.db_cur.execute('''DELETE FROM sources WHERE url=?''', url_tuple)
        except sqlite3.DatabaseError:
            raise
        return True
            
    def touch_source_url(self, url):
        t = (time(), url)
        try:
            self.db_cur.execute('''UPDATE sources SET last_updated=? WHERE url=?''', t)
        except sqlite3.DatabaseError:
            raise
            return False
        return True
    def test_source_url(self, url):
        url_tuple = (str(url),)
        try:
            self.db_cur.execute('''SELECT * FROM sources WHERE url=?''', url_tuple)
        except sqlite3.DatabaseError:
            raise
        if self.db_cur.fetchone() is None:
            return False
        return True

    @staticmethod 
    def sqlite3_db_file_type(pathname):
        with open(pathname, 'rb') as db_file:                         
            header = db_file.read(16)                                 
            if header == b'SQLite format 3\x00':                      
                db_file.close()    
                return pathname
            else:                  
                db_file.close()    
                return False
    @staticmethod
    def sqlite3_db_application_id(pathname):
        with open(pathname, 'rb') as db_file:
            db_file.seek(68)
            # application_id is a uint32 in big endian format
            # using struct.unpack to get the value
            application_id = unpack('>I', db_file.read(4))[0]
            if application_id == 0x722ab81c:
                db_file.close()
                return pathname
            else:
                db_file.close()
                return False

