#! /usr/bin/env python3

import sys
import mailadmin
import MySQLdb


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: %s DOMAIN\nExample: %s example.org' % (sys.argv[0], sys.argv[0]))
        sys.exit(1)
    domain = sys.argv[1]
    if domain.startswith('@'):
        print('Your domain starts with an @, this is probably not what you want (use example.org not @example.org). Error')
        sys.exit(1)
    try:
        db = mailadmin.open_from_settings()
    except MySQLdb.Error as e:
        print('Error while connecting to database:', e)
        sys.exit(1)
    try:
        mailadmin.add_domain(db, domain)
    except MySQLdb.Error as e:
        print('Error:', e)
        sys.exit(1)
    print('Successfully added domain "%s"' % domain)
