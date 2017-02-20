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

import crypt
import MySQLdb
import string
import random
import configparser
import sys

pw_chars = string.ascii_letters + string.digits

def parse_settings(path='.config'):
    config = configparser.ConfigParser()
    config.read(path)
    mysql = config['mysql']
    user = mysql.get('user')
    if user is None:
        print('"user" not set in config file. Error.')
        sys.exit(1)
    password = mysql.get('password')
    if password is None:
        print('"password" not set in config file. Error')
        sys.exit(1)
    host = mysql.get('host', '127.0.1.1')
    port = mysql.getint('port', 3306)
    db = mysql.get('db', 'mailserver')
    return {'host': host, 'port': port, 'db': db, 'user': user, 'password': password}

def gen_pw(pw_len=6):
    return "".join(random.choice(pw_chars) for _ in range(pw_len))

def open_db(host, user, passwd, port=3306, db='mailserver'):
    return MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, port=port)

def open_from_settings(path='.config'):
    settings = parse_settings(path)
    return open_db(host=settings['host'], user=settings['user'], passwd=settings['password'], port=settings['port'], db=settings['db'])

def gen_hash(pw):
    return '{SHA512-CRYPT}' + crypt.crypt(pw, crypt.mksalt(crypt.METHOD_SHA512))

def init_db(db):
    cur = db.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS virtual_domains (
        	id INT NOT NULL AUTO_INCREMENT,
        	name VARCHAR(50) NOT NULL,
        	PRIMARY KEY(id),
        	UNIQUE KEY name (name)
        )
        '''
    )
    cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS virtual_users (
    	id INT NOT NULL AUTO_INCREMENT,
    	domain_id INT NOT NULL,
    	email VARCHAR(100),
    	password varchar(150) NOT NULL,
    	PRIMARY KEY(id),
    	UNIQUE KEY email (email),
    	FOREIGN KEY (domain_id) REFERENCES virtual_domains(id) ON DELETE CASCADE
    )
    '''
    )
    cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS virtual_aliases (
    	id INT NOT NULL AUTO_INCREMENT,
    	domain_id INT NOT NULL,
    	source VARCHAR(100) NOT NULL,
    	destination VARCHAR(100) NOT NULL,
    	PRIMARY KEY (id),
    	FOREIGN KEY (domain_id) REFERENCES virtual_domains(id) ON DELETE CASCADE
    )
    '''
    )
    cur.close()
    db.commit()

def add_domain(db, name):
    cur = db.cursor()
    cmd = '''
    INSERT INTO virtual_domains
    (name)
    VALUES (%s)
    '''
    cur.execute(cmd, (name,))
    cur.close()
    db.commit()

def add_user(db, mail, pw_hash):
    cur = db.cursor()
    split = mail.split('@')
    if len(split) != 2:
        print('Email does not contain exactly one @. Error.')
        sys.exit(1)
    domain = split[1]
    get_domain = '''
    SELECT id FROM virtual_domains WHERE name = %s
    '''
    cur.execute(get_domain, (domain,))
    entries = list(cur)
    if not entries:
        print('Domain "%s" was not found. Error.' % domain)
        sys.exit(1)
    # everything ok, we got the id, so now add
    domain_id = entries[0][0]
    cmd = '''
    INSERT INTO virtual_users
    (domain_id, email, password)
    VALUES (%s, %s, %s)
    '''
    cur.execute(cmd, (domain_id, mail, pw_hash))
    cur.close()
    db.commit()
