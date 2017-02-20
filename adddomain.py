#! /usr/bin/env python3

# Copyright (c) 2016, 2017 Fabian Wenzelmann

# MIT License
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
