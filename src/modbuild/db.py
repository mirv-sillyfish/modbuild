import sqlite3

db_path = None
db_con = None

def db_open(path):
    global db_path
    global db_con

    db_path = path
    db_con = sqlite3.connect(str(path))
    cur = db_con.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS MD5 (
            file TEXT PRIMARY_KEY,
            hash TEXT
        )
        ''')
    db_con.commit()
    cur.close()

def db_close():
    global db_con
    db_con.close()
    db_con = None

def db_query_md5(key):
    global db_con
    cur = db_con.cursor()
    md5 = cur.execute(''' SELECT hash FROM MD5 WHERE file=? ''', (key,)).fetchone()
    cur.close()
    if md5:
        return md5[0]
    else:
        return None

def db_update_md5(key, md5):
    global db_con
    cur = db_con.cursor()
    cur.execute(''' UPDATE MD5 SET hash=? WHERE file=? ''', (md5, key))
    db_con.commit()
    cur.close()

def db_insert_md5(key, md5):
    global db_con
    cur = db_con.cursor()
    cur.execute(''' INSERT INTO MD5 VALUES(?, ?) ''', (key, md5))
    db_con.commit()
    cur.close()

def db_clean():
    global db_con
    cur = db_con.cursor()
    cur.execute(''' DROP TABLE MD5 ''')
    db_con.commit()
    cur.close()
