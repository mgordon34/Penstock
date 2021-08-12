import requests

from db import DB

DB_FILE = '/Users/matt/git/trading/trades.db'
base_url = 'https://data.alpaca.markets/v2'
header = {
  'APCA-API-KEY-ID': 'PK6QQSCLGG19AYT9O9G1',
  'APCA-API-SECRET-KEY': 'QDwHP2TNze94d8Wc1Dg1QDpoJCQq1JDG1nX92wxN'
}

def injest_bars(ticker):
  url = base_url + '/stocks/' + ticker + '/bars?timeframe=1Min&start=2021-08-12T13:30:00Z&end=2021-08-12T19:59:00Z'
  r = requests.get(url, headers=header)

  for bar in r.json()['bars']:
    bar_object = (ticker, bar['o'], bar['h'], bar['l'], bar['c'], bar['v'], bar['t'])
    db.add_bar(bar_object)

def print_bars():
  bars = db.get_all_bars('2021-08-11T13:30:00Z', '2021-08-11T19:59:00Z')
  for bar in bars:
    print(bar)

db = DB(DB_FILE)
# sql_create_bars_table =  """CREATE TABLE IF NOT EXISTS bars (
#                                 id integer PRIMARY KEY,
#                                 ticker text NOT NULL,
#                                 open real NOT NULL,
#                                 high real NOT NULL,
#                                 low real NOT NULL,
#                                 close real NOT NULL,
#                                 volume integer NOT NULL,
#                                 timestamp text NOT NULL
#                               );"""
# db.create_table(sql_create_bars_table)


TICKERS = ['SPY', 'AAPL', 'MSFT', 'TSLA', 'PLUG', 'WKHS', 'BIDU', 'ROKU', 'AMD', 'NVDA',
'TWTR', 'FB', 'NFLX', 'CRSR', 'AMC', 'GME', 'RBLX', 'ATVI', 'BYND', 'JBLU', 'DAL', 'CCL', 
'SNOW', 'SHOP', 'TLRY', 'MRNA', 'PFE', 'DFS', 'WFC', 'JPM', 'RKT', 'WMT', 'F', 'V', 'IYE', 
'XOM']
for ticker in TICKERS:
  injest_bars(ticker)

# tickers = ['BIDU']
# a = db.get_bars(tickers, '2021-07-12T13:30:00Z', '2021-07-12T19:59:00Z')
# c = 0
# for i in a:
#   c += 1
#   print(i)
# print(c)