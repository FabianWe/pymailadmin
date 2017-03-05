# Copyright (c) 2017 Fabian Wenzelmann

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

class SQLExecuteException(Exception):
    pass

def get_domains(db):
    sql_cmd = '''SELECT name FROM virtual_domains'''
    cur = db.cursor()
    cur.execute(sql_cmd)
    for entry in cur.fetchall():
        yield entry[0]
    cur.close()

def add_domain(db, name):
    sql_cmd = '''INSERT INTO virtual_domains (name) VALUES(%s)'''
    cur = db.cursor()
    cur.execute(sql_cmd, (name, ))
    cur.close()
    db.commit()

def remove_domain(db, name):
    sql_cmd = '''DELETE FROM virtual_domains WHERE name=%s'''
    cur = db.cursor()
    cur.execute(sql_cmd, (name,))
    cur.close()
    db.commit()
    if cur.rowcount != 1:
        raise SQLExecuteException('Nothing was deleted from table.')

def get_users(db):
    sql_cmd = '''SELECT email FROM virtual_users'''
    cur = db.cursor()
    cur.execute(sql_cmd)
    for entry in cur.fetchall():
        yield entry[0]
    cur.close()

def add_user(db, mail, pw_hash):
    split = mail.split('@')
    if len(split) != 2:
        raise SQLExecuteException('Email does not contain exactly one @. Error.')
    domain = split[1]
    cur = db.cursor()
    get_domain = 'SELECT id FROM virtual_domains WHERE name=%s'
    cur.execute(get_domain, (domain,))
    entries = list(cur)
    if not entries:
        raise SQLExecuteException('Domain "%s" was not found. Error.' % domain)
    # everything ok, we got the id, so now add
    domain_id = entries[0][0]
    insert_cmd = 'INSERT INTO virtual_users (domain_id, email, password) VALUES (%s, %s, %s)'
    cur.execute(insert_cmd, (domain_id, mail, pw_hash))
    cur.close()
    db.commit()

def change_pw(db, mail, _hash):
    update_cmd = 'UPDATE virtual_users SET password=%s WHERE email=%s'
    cur = db.cursor()
    cur.execute(update_cmd, (_hash, mail))
    cur.close()
    db.commit()
    if cur.rowcount != 1:
        raise SQLExecuteException('Update effected no entry in the database')

def remove_user(db, mail):
    sql_cmd = 'DELETE FROM virtual_users WHERE email=%s'
    cur = db.cursor()
    cur.execute(sql_cmd, (mail,))
    cur.close()
    db.commit()
    if cur.rowcount != 1:
        raise SQLExecuteException('Nothing was deleted from table.')

def get_aliases(db):
    sql_cmd = 'SELECT source, destination FROM virtual_aliases'
    cur = db.cursor()
    cur.execute(sql_cmd)
    for entry in cur.fetchall():
        yield entry
    cur.close()

def remove_alias(db, source, dest):
    sql_cmd = 'DELETE FROM virtual_aliases WHERE (source=%s AND destination=%s)'
    cur = db.cursor()
    cur.execute(sql_cmd, (source, dest))
    cur.close()
    db.commit()
    if cur.rowcount != 1:
        raise SQLExecuteException('Nothing was deleted from table.')

def add_alias(db, source, dest):
    split = source.split('@')
    if len(split) != 2:
        raise SQLExecuteException('Email does not contain exactly one @. Error.')
    domain = split[1]
    cur = db.cursor()
    get_domain = 'SELECT id FROM virtual_domains WHERE name=%s'
    cur.execute(get_domain, (domain,))
    entries = list(cur)
    if not entries:
        raise SQLExecuteException('Domain "%s" was not found. Error.' % domain)
    domain_id = entries[0][0]
    # insert
    add_cmd = '''INSERT INTO virtual_aliases
                 (domain_id, source, destination)
                 VALUES(%s, %s, %s)'''
    cur.execute(add_cmd, (domain_id, source, dest))
    cur.close()
    db.commit()
