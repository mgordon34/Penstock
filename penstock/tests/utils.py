import os
import shutil
import sqlite3

TEMPLATE_FILE = '../data/template_data.db'
DB_FILE = '../data/test_data.db'

def setup_test_db():
    print('copying db')
    db_file = DB_FILE
    shutil.copy(TEMPLATE_FILE, db_file)
    return db_file

def teardown_test_db():
    print('tearing down db')
    os.remove(DB_FILE)