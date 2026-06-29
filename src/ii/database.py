import sqlite3
import json
from datetime import datetime

DB_NAME = 'ii.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        create table if not exists requests (
            id integer primary key autoincrement,
            timestamp text,
            total_objects integer,
            cats integer,
            dogs integer,
            couches integer,
            violations integer
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(timestamp, total_objects, cats, dogs, couches, violations):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        insert into requests (timestamp, total_objects, cats, dogs, couches, violations)
        values (?, ?, ?, ?, ?, ?)
    ''', (timestamp, total_objects, cats, dogs, couches, violations))
    
    conn.commit()
    conn.close()

def get_records():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('select * from requests order by id desc')
    rows = cursor.fetchall()
    conn.close()
    return rows

init_db()