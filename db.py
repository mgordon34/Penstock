import sqlite3
from sqlite3 import Error

import config
from log import log

class DB(object):
  def __init__(self, db_file):
    self.conn = self.create_connection(db_file)

    sql_create_trades_table =  """CREATE TABLE IF NOT EXISTS trades (
                                    id integer PRIMARY KEY,
                                    ticker text NOT NULL,
                                    price real NOT NULL,
                                    size integer NOT NULL,
                                    timestamp text NOT NULL
                                  );"""
    sql_create_bars_table =  """CREATE TABLE IF NOT EXISTS bars (
                                    id integer PRIMARY KEY,
                                    ticker text NOT NULL,
                                    open real NOT NULL,
                                    high real NOT NULL,
                                    low real NOT NULL,
                                    close real NOT NULL,
                                    volume integer NOT NULL,
                                    timestamp text NOT NULL
                                  );"""
    self.create_table(sql_create_trades_table)
    self.create_table(sql_create_bars_table)

  def create_connection(self, db_file):
    conn = None
    try:
      conn = sqlite3.connect(db_file, check_same_thread=False)
      conn.isolation_level = None
      log.debug('DB connection established version: ' + sqlite3.version)
    except Error as e:
      log.error(e)
    
    return conn

  def create_table(self, create_table_sql):
    try:
      c = self.conn.cursor()
      c.execute(create_table_sql)
    except Error as e:
      log.error(e)

  def add_trade(self, trade):
    sql = '''INSERT INTO trades(ticker,price,size,timestamp)
              VALUES(?,?,?,?)'''
    cur = self.conn.cursor()
    cur.execute(sql, trade)
    self.conn.commit()
    return cur.lastrowid

  def add_bar(self, bar):
    sql = '''INSERT INTO bars(ticker,open,high,low,close,volume,timestamp)
              VALUES(?,?,?,?,?,?,?)'''
    cur = self.conn.cursor()
    cur.execute(sql, bar)
    self.conn.commit()
    return cur.lastrowid

  def bulk_add_bars(self, bars):
    sql = '''INSERT INTO bars(ticker,open,high,low,close,volume,timestamp)
              VALUES(?,?,?,?,?,?,?)'''
    cur = self.conn.cursor()
    try:
      cur.execute('begin')
      for bar in bars:
        cur.execute(sql, bar)
      cur.execute('commit')
      log.debug(cur.lastrowid)
    except Error as e:
      log.error(e)
      cur.execute('rollback')

  
  def get_bars(self, tickers, start, end):
    ticker_str = ''
    for ticker in tickers:
      s = "'" + ticker + "', "
      ticker_str += s
    sql = '''SELECT * FROM bars WHERE ticker IN ({}) AND datetime(timestamp) BETWEEN datetime('{}') AND datetime('{}') ORDER BY datetime(timestamp)'''
    sql = sql.format(ticker_str[:-2], start, end)
    cur = self.conn.cursor()
    cur.execute(sql)
    return cur.fetchall()
  
  def get_all_bars(self, start, end):
    sql = '''SELECT * FROM bars WHERE datetime(timestamp) BETWEEN datetime('{}') AND datetime('{}') ORDER BY datetime(timestamp)'''
    sql = sql.format(start, end)
    cur = self.conn.cursor()
    cur.execute(sql)
    return cur.fetchall()

  def get_bars_and_trades(self,  tickers, start, end):
    ticker_str = ''
    for ticker in tickers:
      s = "'" + ticker + "', "
      ticker_str += s
    bar_sql = '''SELECT * FROM bars WHERE ticker IN ({}) AND datetime(timestamp) BETWEEN datetime('{}') AND datetime('{}')'''
    bar_sql = bar_sql.format(ticker_str[:-2], start, end)
    trade_sql = '''SELECT * FROM bars WHERE datetime(timestamp) BETWEEN datetime('{}') AND datetime('{}') ORDER BY datetime(timestamp)'''
    trade_sql = trade_sql.format(start, end)
    sql = bar_sql + ' UNION ALL ' + trade_sql
    cur = self.conn.cursor()
    cur.execute(sql)
    return cur.fetchall()
    
# Test function
if __name__ == '__main__':
  a = [{"T":"t","i":8207,"S":"TSLA","x":"V","p":648.15,"s":15,"c":["@","I"],"z":"C","t":"2021-07-08T17:18:28.04582059Z"}]
  a = a[0]
  trade = (a['S'], a['p'], a['s'], a['t'])
  db = DB(config.db_file)
  db.add_trade(trade)
  '''select * from bars where datetime(timestamp) between datetime('2021-07-12T13:30:00Z') and datetime('2021-07-12T19:59:00Z')'''