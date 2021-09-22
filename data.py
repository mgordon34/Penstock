import requests
import datetime
import logging

from db import DB
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

DB_FILE = '/Users/matt/git/trading/trades.db'
base_url = 'https://data.alpaca.markets/v2'
header = {
  'APCA-API-KEY-ID': 'PK6QQSCLGG19AYT9O9G1',
  'APCA-API-SECRET-KEY': 'QDwHP2TNze94d8Wc1Dg1QDpoJCQq1JDG1nX92wxN'
}

def injest_bars(symbols, dates):
  for date in dates:
    bars = []
    for symbol in symbols:

      url = base_url + '/stocks/' + symbol + '/bars?timeframe=1Min&start=' +date+ 'T13:30:00Z&end=' + date + 'T19:59:00Z'
      r = requests.get(url, headers=header)

      try:
        for bar in r.json()['bars']:
          bar_object = (symbol, bar['o'], bar['h'], bar['l'], bar['c'], bar['v'], bar['t'])
          bars.append(bar_object)
      except:
        print(r.text)
    db.bulk_add_bars(bars)

def print_bars():
  bars = db.get_all_bars('2021-08-13T13:30:00Z', '2021-08-13T19:59:00Z')
  for bar in bars:
    print(bar)
  print(len(bars))

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


SYMBOLS = ['SPY', 'AAPL', 'MSFT', 'TSLA', 'PLUG', 'WKHS', 'BIDU', 'ROKU', 'AMD', 'NVDA',
'TWTR', 'FB', 'NFLX', 'CRSR', 'AMC', 'GME', 'RBLX', 'ATVI', 'BYND', 'JBLU', 'DAL', 'CCL', 
'SNOW', 'SHOP', 'TLRY', 'MRNA', 'PFE', 'DFS', 'WFC', 'JPM', 'RKT', 'WMT', 'F', 'V', 'IYE', 
'XOM']
curr_date = datetime.datetime.strptime('2021-09-20', '%Y-%m-%d').date()
dates = []
for i in range(1,4):
  if curr_date.isoweekday() in range(1,6):
    dates.append(curr_date.strftime('%Y-%m-%d'))
  curr_date = curr_date + datetime.timedelta(days=1)
print(len(dates))

# TICKERS = ['TSLA']
injest_bars(SYMBOLS, dates)
# print_bars()

# tickers = ['BIDU']
# a = db.get_bars(tickers, '2021-07-12T13:30:00Z', '2021-07-12T19:59:00Z')
# c = 0
# for i in a:
#   c += 1
#   print(i)
# print(c)