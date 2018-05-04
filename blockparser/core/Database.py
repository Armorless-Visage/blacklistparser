#!/usr/bin/env python
# Liam Nolan (c) 2018

from sys import stderr, exit
from os import urandom, path
from time import time
from blockparser.core import Exceptions
import sqlite3

class Manager:
    def __init__(self, db_path=None):
        '''
        - opens a connection to a sqlite3 db (or creates a new one)
        - open connection is at self.db
        - db_path is the pathname of the sqlite3 database
        - set create_new_db to True to create a new empty sqlite3 db
        '''
        self.db_conn = self.connect_to_db(db_path)

    def connect_to_db(self, db_path=None):
        if path.isfile(db_path):
            # check file is sqlite3 format
            if Utilities.sqlite3_db_file_type(db_path) is False:
                errmsg = 'Existing file ' + str(db_path) + ' is not a sqlite3 database'
                raise Exceptions.BadFileType(errmsg)
            # check file has the right application_id for blocklistparser
            if Utilities.sqlite3_db_application_id(db_path) is False:
                errmsg = 'File is a sqlite3 db, but the application_id is not correct'
                raise Exceptions.BadFileType(errmsg)
        try:
            db_conn = sqlite3.connect(db_path)
            self.init_db(db_conn)
        except sqlite3.OperationalError or sqlite3.DatabaseError:
            # TODO insert exception handling here
            #      - permissions check, symlink, path
            raise

        return db_conn

    def init_db(self, db_conn):
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
        application_id = ("PRAGMA application_id = 0x722ab81c")
        user_version = ("PRAGMA user_version = 0x1")
        cur = db_conn.cursor()
        try:
            cur.execute(source_table)
            cur.execute(data_table)
            cur.execute(application_id)
            cur.execute(user_version)
            db_conn.commit()
            return True
        except sqlite3.DatabaseError:
            raise
        
    
class Utilities:
    def pull_names(db_conn):
        '''
        returns a list of tuples of elements name, rowid from the input table
        select arg is passed as where=? to sqlite3
        '''
        line = (" SELECT name, rowid FROM data ")
        cur = db_conn.cursor()
        cur.execute(line)
        return cur.fetchall()
    
    def pull_names_within_timout(timeout, db_conn):
        '''
        returns a list of tuples of elements name, rowid from the input table
        select arg is passed as where=? to sqlite3
        '''
        join = (timeout, time())
        line = (' SELECT name FROM data WHERE last_seen + ? >= ? ')
        cur = db_conn.cursor()
        cur.execute(line)
        return cur.fetchall()
    
    def pull_active_source_urls(db_conn):
        '''
        return a list of the blacklist urls that need updating from sources
        '''
        ctime = (time(),)
        cur = db_conn.cursor()
        cur.execute('''SELECT url FROM sources WHERE ? >= last_updated + timeout''', ctime)
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
        
    def bulk_add(db_conn, data_lst, source_url):
        '''
        add a list of items to the db using executemany
        ! Does not validate do it elsewhere TODO integrate val here
        ! Does not explicitly commit
        '''
        cur = db_conn.cursor()

        joined = []
        time_update = []
        current_time = time()
         
        # check there is something to add then format and add them all using executemany
        if (len(validated_lst) < 1):
            errmsg = 'No items to add.'
            raise Exceptions.EmptyList(errmsg) 
        for each in data_lst:
            strip = each.rstrip()
            joined.append((strip, current_time, current_time, source_url))
            time_update.append((current_time, source_url, strip))
        
        iline = (" INSERT OR IGNORE INTO data" +
                " VALUES ( ?, ?, ?, ? )")
        cur.executemany(iline, joined)
        tline = (" UPDATE " + table_name + 
                " SET last_seen=?, source=? WHERE name=? ")
        executemany(tline, time_update)
        #NOTE: this code above only writes the last url w/ addr to source
        return True
    
    def add_element(db_conn, table_name, address, source):
        '''
        add a single element to the db
        NOTE: this checks time.time() every time it is executed, probably
        going to be very slow if it's called lots
        '''
        cur = db_conn.cursor()
        if type(address) is not str:
            raise Exceptions.NotString('address must be a string')
        strip = address.rstrip()
        # this will either be a valid ip or None
        # format the sqlite3 input
        current_time = time()
        t = ( str(validated_addr), current_time, current_time, str(source) ) 
        u = ( current_time, str(source), str(validated_addr) )
        
        line = (" INSERT OR IGNORE INTO data" +
                " VALUES ( ?, ?, ?, ? ) ")
        uline = (" UPDATE data" +
            " SET last_seen=?, source=? WHERE name=?")
        cur.execute(line, t)
        cur.execute(uline, u)
    
    def add_source_url(db_conn, url, table_name, timeout):
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
    
        cur = db_conn.cursor()
        # url, source page format, page update timeout,
        # last_updated set to 61sec after epoch (never)
        t = ( str(url), str(table_name), float(timeout), float(61) )
        
        try:
            cur.execute('''INSERT OR IGNORE INTO sources VALUES ( ?, ?, ?, ? )''', t)
        except DatabaseError:
            raise
            return False
        return True

    def delete_source_url(db_conn, url):
        '''
        delete a blacklist source url from the database
        '''
        cur = db_conn.cursor()
        try:
            cur.execute('''DELETE FROM sources WHERE url=?''', url)
        except DatabaseError:
            raise
            return False
        return True
            
    def touch_source_url(db_conn, url):
        t = (time(), url)
        try:
            cur.execute('''UPDATE sources SET last_updated=? WHERE url=?''', t)
        except DatabaseError:
            raise
            return false
        return True
   
    def sqlite3_db_file_type(pathname):
        with open(pathname, 'rb') as db_file:                         
            header = db_file.read(16)                                 
            if header == b'SQLite format 3\x00':                      
                db_file.close()    
                return pathname
            else:                  
                db_file.close()    
                return False       
    def sqlite3_db_application_id(pathname):
        with open(pathname, 'rb') as db_file:
            application_id = db_file.seek(68).read(4)
            if application_id == 0x722ab81c:
                db_file.close()
                return pathname
            else:
                db_file.close()
                return False

