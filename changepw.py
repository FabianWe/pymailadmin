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

def get_user_id(db, mail):
    get_user = '''
    SELECT id FROM virtual_users WHERE email = %s
    '''
    cur = db.cursor()
    cur.execute(get_user, (mail,))
    cur.close()
    entries = list(cur)
    if not entries:
        print('No email "%s" found in the database. Error.' % mail)
        sys.exit(1)
    return entries[0][0]

def update_user(db, mail_id, _hash):
    cmd = '''
    UPDATE virtual_users
    SET password=%s
    WHERE id=%s
    '''
    cur = db.cursor()
    cur.execute(cmd, (_hash, mail_id))
    assert cur.rowcount == 1
    cur.close()
    db.commit()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: %s MAIL' % sys.argv[0])
        sys.exit(1)
    mail = sys.argv[1]
    try:
        db = mailadmin.open_from_settings()
    except MySQLdb.Error as e:
        print('Error while connecting to database:', e)
        sys.exit(1)
    try:
        mail_id = get_user_id(db, mail)
    except MySQLdb.Error as e:
        print('Error while accessing database:', e)
        sys.exit(1)
    pw1 = getpass.getpass()
    pw2 = getpass.getpass(prompt='Repeat password: ')
    if pw1 != pw2:
        print("The passwords didn't match", file=sys.stderr)
        sys.exit(1)
    pw = pw1
    _hash = mailadmin.gen_hash(pw)
    try:
        update_user(db, mail_id, _hash)
    except MySQLdb.Error as e:
        print("Error while updating the database:", e)
        sys.exit(1)
    print('Update successful')
