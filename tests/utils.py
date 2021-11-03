import os
import shutil
import sqlite3

DB_FILE = 'test_data.db'

def setup_test_db():
    print('copying db')
    db_file = DB_FILE
    shutil.copy('data_template.db', db_file)
    return db_file

def teardown_test_db():
    print('tearing down db')
    os.remove(DB_FILE)