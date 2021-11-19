from abc import abstractmethod
import websocket
import json
import threading
import traceback
import queue
from time import sleep, time
from collections import defaultdict

import common.config as config
from db import DB
from event import MarketEvent

import logging
log = logging.getLogger(__name__)
log.addHandler(config.handler)

class OutofDataError(Exception):
  pass

class TickerObject(object):
  def __init__(self):
    self.hod = None
    self.lod = None
    self.price = None
    self.bars = []

  def update_price(self, price, timestamp):
    self.price = price
    if not self.hod or price > self.hod[0]:
      self.hod = (price, timestamp)
    if not self.lod or price < self.lod[0]:
      self.lod = (price, timestamp)

  def add_bar(self, bar):
    if not self.hod or bar['h'] > self.hod[0]:
      self.hod = (bar['h'], bar['t'])
    if not self.lod or bar['l'] < self.lod[0]:
      self.lod = (bar['l'], bar['t'])

    self.bars.append(bar)


class DataHandler(object):
  def __init__(self, db_file_name, events):
    self.db = DB(db_file_name)
    self.events = events
    self.tickers = defaultdict(TickerObject)

  def get_latest_bars(self, ticker, N=1):
    return self.tickers[ticker].bars[-N:]
  
  @abstractmethod
  def update_price(self):
    raise NotImplementedError('update_price() should be implemented')

class HistoricalDataStreamer(DataHandler):
  def __init__(self, db_file_name, events, type, tickers, start, end):
      super().__init__(db_file_name, events)
      self.type = type
      self.data = queue.Queue()
      self.index = -1
      self.load_data(type, tickers, start, end)

  def get_latest_bars(self, ticker, N=1):
    start = self.index-N+1
    if (start < 0):
      start = 0
    return self.tickers[ticker].bars[start:self.index+1]

  def update_price(self):
    if self.type == 'bars':
      self.index += 1
      if self.index < self.len:
        self.events.put(MarketEvent('bars'))
      else:
        raise OutofDataError

  def load_data(self, type, tickers, start, end):
    if type == 'bars':
      self.len = 0
      dbdata = self.db.get_bars(tickers, start, end)
      for ticker in tickers:
        bars = self.fix_bars(ticker, dbdata)
        self.tickers[ticker].bars = bars
        if len(bars) > self.len:
          self.len = len(bars)
      self.data.queue = queue.deque(bars)
  
  def fix_bars(self, symbol, bars):
    ret = []
    for bar in bars:
      if (bar[1] == symbol):
        a = {
          'o': bar[2],
          'h': bar[3],
          'l': bar[4],
          'c': bar[5],
          'v': bar[6],
          't': bar[7],
        }
        ret.append(a)
    return ret


class LiveDataStreamer(DataHandler):
  def __init__(self, db_file_name, events, bars_to_watch, trades_to_watch=[]):
    super().__init__(db_file_name, events)
    self.bars_to_watch = bars_to_watch
    self.trades_to_watch = trades_to_watch
    self.ws = websocket.WebSocketApp(config.ws_url, on_open=self.on_open, on_message=self.on_message, on_close=self.on_close)
    self.wst = threading.Thread(target=self.ws.run_forever)
    self.wst.daemon = True
    self.new_bar = False
    self.new_trade = False
    self.bars_to_add = []

  def update_price(self):
    if self.new_bar and (time() - self.new_bar) > 2:
      self.new_bar = False
      self.events.put(MarketEvent('bars'))
    if self.new_trade:
      self.new_trade = False
      self.events.put(MarketEvent('trade'))
  
  def get_price(self, symbol):
    return self.tickers[symbol].price

  def on_open(self, ws):
    log.debug("Live WS opened")
    auth_data = {"action": "auth", "key": config.alpaca_api_key, "secret": config.alpaca_api_secret}

    ws.send(json.dumps(auth_data))

    subscribe_message = {"action": "subscribe", "bars": self.bars_to_watch, "trades": self.trades_to_watch}

    ws.send(json.dumps(subscribe_message))

  def on_message(self, ws, message):
    log.debug('handling message: ' + message)
    message = json.loads(message)
    print(message)
    self.handle_message(message)

  def on_close(self, ws):
    log.debug("closed connection")

  def subscribe_to_ticker(self, tickers):
    log.debug(f'subscribing from {tickers}')
    subscribe_message = {"action": "subscribe", "trades": tickers}
    self.ws.send(json.dumps(subscribe_message))

  def unsubscribe_to_ticker(self, tickers):
    log.debug(f'unsubscribing from {tickers}')
    unsubscribe_message = {"action": "unsubscribe", "trades": tickers}
    self.ws.send(json.dumps(unsubscribe_message))

  def handle_message(self, message):
    for event in message:
      type = event['T']
      if type == 't':
        self.handle_trade(event)
      elif type == 'b':
        self.handle_bar(event)

  def handle_trade(self, trade):
    try:
      log.debug('Handling trade for ' + trade['S'])
      trade_obj = (trade['S'], trade['p'], trade['s'], trade['t'])
      self.db.add_trade(trade_obj)
      self.tickers[trade['S']].update_price(trade['p'], trade['t'])
      self.new_trade = True
    except Exception as e:
      log.error('error')
      log.error(traceback.print_exc())


  def handle_bar(self, bar):
    try:
      log.debug('Handling bar for ' + bar['S'])
      s = bar['S']
      bar_obj = (bar['o'], bar['h'], bar['l'], bar['c'], bar['v'], bar['t'])
      self.db.add_bar((s, *bar_obj))
      b = {
        'o': bar['o'],
        'h': bar['h'],
        'l': bar['l'],
        'c': bar['c'],
        't': bar['t']
      }
      self.tickers[s].add_bar(b)
      self.new_bar = time()
    except Exception as e:
      log.error('error')
      log.error(traceback.print_exc())

  def run(self):
    self.wst.start()

if __name__ == '__main__':
  events = None
  stream = LiveDataStreamer(events)
  stream.run()

  conn_timeout = 5
  while not stream.ws.sock.connected and conn_timeout:
    sleep(1)
    conn_timeout -= 1

  msg_counter = 0
  while stream.ws.sock.connected:
    sleep(1)
