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
import getpass
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Adds a new mail user.',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        'mail',
        help='The new E-Mail (name@domain)',
        metavar='MAIL'
    )
    parser.add_argument(
        '--genpw',
        help='If set to true a random password will be generated and printed out',
        action='store_true',
        required=False)
    parser.add_argument(
        '--password',
        '-p',
        help='Set the password for the user',
        metavar='PASSWORD',
        required=False)
    args = parser.parse_args()
    pw = None
    if args.genpw and args.password is not None:
        print("You can't create a random password and set it as well... Use --help for a help text.", file=sys.stderr)
        sys.exit(1)
    elif not args.genpw and args.password is None:
        pw1 = getpass.getpass()
        pw2 = getpass.getpass(prompt='Repeat password: ')
        if pw1 != pw2:
            print("The passwords didn't match", file=sys.stderr)
            sys.exit(1)
        pw = pw1
    elif args.genpw:
        pw = mailadmin.gen_pw()
        print('Created random password:', pw)
    else:
        pw = args.password
    _hash = mailadmin.gen_hash(pw)
    assert len(_hash) == 120
    mail = args.mail
    try:
        db = mailadmin.open_from_settings()
    except MySQLdb.Error as e:
        print('Error while connecting to database:', e)
        sys.exit(1)
    try:
        mailadmin.add_user(db, mail, _hash)
    except MySQLdb.Error as e:
        print('Error while adding user:', e)
        sys.exit(1)
    print("Done")
