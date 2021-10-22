import sqlite3
from sqlite3 import Error
from flask import g

def get_db():
    try: 
        if 'db' not in g:
            g.db=sqlite3.connect('aeropuerto.db')
        return g.db
    except Error:
        print(Error)
        

def close_db():
    db = g.pop( 'db', None )
    if db is not None:
        db.close()