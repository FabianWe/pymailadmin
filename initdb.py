#! /usr/bin/env python3

import sys
import mailadmin
import MySQLdb

if __name__ == '__main__':
    try:
        db = mailadmin.open_db('127.0.1.1', 'root', 'DaV70xcLjjM4ARm9fmIxwgOjRClDXmzv')
    except MySQLdb.Error as e:
        print("Error while opening db: %s" % str(e), file=sys.stderr)
        sys.exit(1)
    print('Initializing the database...')
    try:
        mailadmin.init_db(db)
    except MySQLdb.Error as e:
        print("Error while Initializing database: %s" % str(e), file=sys.stderr)
        sys.exit(1)
