import crypt
import MySQLdb
import string
import random

pw_chars = string.ascii_letters + string.digits

def gen_pw(pw_len=6):
    return "".join(random.choice(pw_chars) for _ in range(pw_len))

def open_db(host, user, passwd, port=3306, db='mailserver'):
    return MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, port=port)

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


def add_user(db, name, pw):
    cur = db.cursor()
