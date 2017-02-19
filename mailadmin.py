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
    db.commit()

def add_domain(db, name):
    cur = db.cursor()
    cmd = '''
    INSERT INTO virtual_domains
    (name)
    VALUES (%s)
    '''
    cur.execute(cmd, (name,))
    db.commit()

def add_user(db, name, pw):
    cur = db.cursor()
