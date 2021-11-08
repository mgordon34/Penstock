from collections import defaultdict
from datetime import datetime
import logging

import common.config as config
import common.utils.stock_data as stock_data
from event import SignalEvent
from strategy import BaseStrategy

log = logging.getLogger(__name__)


def diff_minutes(old, new):
  if not old:
    return -1
  old = datetime.strptime(old, "%Y-%m-%dT%H:%M:%SZ")
  new = datetime.strptime(new, "%Y-%m-%dT%H:%M:%SZ")
  ret = abs((old-new).total_seconds()/60)
  return ret

def find_lowest(bars):
  low = (float('+inf'), None)
  for bar in bars:
    if bar['l'] < low[0]:
      low = (bar['l'], bar['t'])
  return low

class ThreeBarTickerObject(BaseStrategy):
  def __init__(self):
    self.ignition = False
    self.pullback = False
    self.hod = None
    self.lod = None

class ThreeBarStrategy(object):
  def __init__(self, events, data):
    self.subscriptions = {'AAPL', 'TSLA', 'BIDU', 'ROKU'}
    self.tickers = defaultdict(ThreeBarTickerObject)
    self.events = events
    self.data = data
    self.positions = defaultdict(dict)

    # for symbol in self.data.tickers:
    #   self.tickers[symbol].hod = (stock_data.get_last_close(symbol), None)

  def handle_mkt_event(self, event):
    if event.mkt_type == 'bars':
      for ticker in self.data.tickers:
        self.calculate_signal(ticker)
    elif event.mkt_type == 'trade':
      return
      log.debug('strat found a trade')
      for ticker in self.subscriptions:
        log.debug('{} price: {}'.format(ticker, self.data.tickers[ticker].price))
    return

  def calculate_signal(self, ticker):
    lookback = 5
    t_obj = self.tickers['ticker']
    bars = self.data.get_latest_bars(ticker, lookback)
    curr_bar = self.data.get_latest_bars(ticker)

    # Skip strategy calls if ticker is out of bars
    if len(bars) == 0 or not curr_bar:
      log.debug('{} is out of bars, not running'.format(ticker))
      return
    curr_bar = curr_bar[0]

    # Calculate bar stats
    if (not self.tickers[ticker].hod or curr_bar['h'] > self.tickers[ticker].hod[0]):
      self.tickers[ticker].hod = (curr_bar['h'], curr_bar['t'])
    if (not self.tickers[ticker].lod or curr_bar['l'] < self.tickers[ticker].lod[0]):
      self.tickers[ticker].lod = (curr_bar['l'], curr_bar['t'])

    # Make sure ticker has reached maturity before generating signals
    if len(bars) < lookback:
      log.debug('{} has not reached lookback length({}), not running'.format(ticker, lookback))
      return
    # log.debug('{} has reached maturity, running strat: {}'.format(ticker, bars))

    # See if position needs to be closed
    if self.positions[ticker]:
      if curr_bar['l'] < self.positions[ticker]['sl']:
        self.positions[ticker] = None
        self.events.put(SignalEvent(ticker, 'CLOSE', curr_bar['l'], curr_bar['t']))
      elif curr_bar['h'] > self.positions[ticker]['tp']:
        self.positions[ticker] = None
        self.events.put(SignalEvent(ticker, 'CLOSE', curr_bar['h'], curr_bar['t']))

    #calculate ignition
    diff = diff_minutes(self.tickers[ticker].hod[1], curr_bar['t'])
    if diff == 0:
      log.debug('new high for {}: {}'.format(ticker, curr_bar))
      qual = True
      for i in range(len(bars)-3, len(bars)):
        if bars[i]['h'] < bars[i-1]['h']:
          qual = False
      if qual:
        log.debug('[{}]Ignition activated for {}'.format(curr_bar['t'], ticker))
        dist = curr_bar['h'] - find_lowest(bars)[0]
        if dist > 0:
          self.tickers[ticker].ignition = {'h': curr_bar['h'], 't': curr_bar['t'], 'dist': dist}
          self.tickers[ticker].pullback = False
    # else:
    #   log.debug('no high({}) for {}: {}'.format(self.tickers[ticker].hod[0], ticker, curr_bar['t']))
    
    if self.tickers[ticker].ignition and diff_minutes(self.tickers[ticker].ignition['t'], curr_bar['t']) > 0:
      #calculate if signal should be generated
      if self.tickers[ticker].pullback and curr_bar['h'] > bars[lookback-2]['h']:
        entry = bars[lookback-2]['h']
        sl = bars[lookback-2]['l']
        tp = self.tickers[ticker].ignition['h']
        # tp = entry + entry * .005
        # tp = max(entry + entry * .005, self.tickers[ticker].ignition['h'])
        log.debug('-------------Trade Found-----------')
        log.debug('[{}]Signal triggered for {} at {}'.format(curr_bar['t'], ticker, entry))
        log.debug('[{}]Stoploss set at {}'.format(curr_bar['t'], sl))
        log.debug('[{}]Take Profit set at {}'.format(curr_bar['t'], tp))
        log.debug('-----------------------------------')
        self.tickers[ticker].ignition = False
        self.tickers[ticker].pullback = False
        if not self.positions[ticker]:
          self.positions[ticker] = {
            "sl": sl,
            "tp": tp
          }
          self.events.put(SignalEvent(ticker, 'BUY', entry, curr_bar['t'], sl, tp))
        return

      #calculate if pullback should be activated
      if curr_bar['h'] < bars[len(bars)-2]['h'] and curr_bar['c'] < curr_bar['o']:
        log.debug('[{}]Pullback activated for {}'.format(curr_bar['t'], ticker))
        self.tickers[ticker].pullback = True

      # calculate if ignition/pullback should be removed
      diff = diff_minutes(self.tickers[ticker].ignition['t'], curr_bar['t'])
      pb_len = self.tickers[ticker].ignition['h'] - curr_bar['l']
      if (diff > 4):
        log.debug('[{}]Ignition/pullback removed for {}: ignition too old'.format(curr_bar['t'], ticker))
        self.tickers[ticker].ignition = False
        self.tickers[ticker].pullback = False
      elif (pb_len/self.tickers[ticker].ignition['dist'] > .75):
        log.debug('[{}]Ignition/pullback removed for {}: pullback too large'.format(curr_bar['t'], ticker))
        log.debug(self.tickers[ticker].ignition['dist'])
        log.debug(pb_len)
        log.debug(self.tickers[ticker].ignition['h'])
        log.debug(curr_bar['l'])
        self.tickers[ticker].ignition = False
        self.tickers[ticker].pullback = False



    # [bar[0]<bar[1] for bar in bars]
    return


class LiveThreeBarStrategy(BaseStrategy):
  def __init__(self, events, data):
    self.subscriptions = {}
    self.tickers = defaultdict(ThreeBarTickerObject)
    self.events = events
    self.data = data
    self.positions = defaultdict(dict)

  def handle_mkt_event(self, event):
    if event.mkt_type == 'bars':
      log.debug('handling bars event')
      for symbol in self.data.tickers:
        self.calculate_signal(symbol)
    elif event.mkt_type == 'trade':
      log.debug('handling trade event')
      for symbol in self.subscriptions:
        if self.subscriptions[symbol] and self.data.get_price(symbol):
          log.debug('{} price: {}'.format(symbol, self.data.get_price(symbol)))
          self.calculate_trade(symbol)
    return

  def unsubscribe(self, symbol):
        self.tickers[symbol].ignition = False
        self.tickers[symbol].pullback = False
        self.positions.pop(symbol, None)
        self.subscriptions.pop(symbol, None)
        self.data.unsubscribe_to_ticker([symbol])


  def calculate_trade(self, symbol):
    price = self.data.get_price(symbol)
    time = datetime.now().isoformat()

    if self.positions[symbol]:
      # See if position needs to be closed
      log.debug(f'{symbol} price: {price}')
      log.debug(f'{symbol} stoploss: {self.positions[symbol]["sl"]}')
      if price < self.positions[symbol]['sl']:
        self.unsubscribe(symbol)
        self.events.put(SignalEvent(symbol, 'CLOSE', price, time))
      elif price > self.positions[symbol]['tp']:
        self.unsubscribe(symbol)
        self.events.put(SignalEvent(symbol, 'CLOSE', price, time))
    else:
      # See if signal should be generated
      if price > self.subscriptions[symbol]['entry']:
        self.tickers[symbol].ignition = False
        self.tickers[symbol].pullback = False
        sl = self.subscriptions[symbol]['sl']
        tp = self.subscriptions[symbol]['tp']
        self.positions[symbol] = {
          'sl': sl,
          'tp': tp
        }

        log.debug(f'Buy signal triggered for {symbol}: at {price}, sl: {sl}, tp: {tp}')
        self.events.put(SignalEvent(symbol, 'BUY', price, time, sl, tp))

  def calculate_signal(self, ticker):
    lookback = 5
    t_obj = self.tickers['ticker']
    bars = self.data.get_latest_bars(ticker, lookback)
    curr_bar = self.data.get_latest_bars(ticker)

    # Skip strategy calls if ticker is out of bars
    if len(bars) == 0 or not curr_bar:
      log.debug('{} is out of bars, not running'.format(ticker))
      return
    curr_bar = curr_bar[0]

    # Calculate bar stats
    if (not self.tickers[ticker].hod or curr_bar['h'] > self.tickers[ticker].hod[0]):
      self.tickers[ticker].hod = (curr_bar['h'], curr_bar['t'])
    if (not self.tickers[ticker].lod or curr_bar['l'] < self.tickers[ticker].lod[0]):
      self.tickers[ticker].lod = (curr_bar['l'], curr_bar['t'])

    # Make sure ticker has reached maturity before generating signals
    if len(bars) < lookback:
      log.debug('{} has not reached lookback length({}), not running'.format(ticker, lookback))
      return
    # log.debug('{} has reached maturity, running strat: {}'.format(ticker, bars))

    # Calculate ignition
    diff = diff_minutes(self.tickers[ticker].hod[1], curr_bar['t'])
    if diff == 0:
      log.debug('new high for {}: {}'.format(ticker, curr_bar))
      qual = True
      for i in range(len(bars)-3, len(bars)):
        if bars[i]['h'] < bars[i-1]['h']:
          qual = False
      if qual:
        log.debug('[{}]Ignition activated for {}'.format(curr_bar['t'], ticker))
        dist = curr_bar['h'] - find_lowest(bars)[0]
        if dist > 0:
          self.tickers[ticker].ignition = {'h': curr_bar['h'], 't': curr_bar['t'], 'dist': dist}
          self.tickers[ticker].pullback = False
    
    if self.tickers[ticker].ignition and diff_minutes(self.tickers[ticker].ignition['t'], curr_bar['t']) > 0:
      #calculate if pullback should be activated
      if curr_bar['h'] < bars[len(bars)-2]['h'] and curr_bar['c'] < curr_bar['o']:
        log.debug('[{}]Pullback activated for {}, subscribing'.format(curr_bar['t'], ticker))
        self.tickers[ticker].pullback = True
        self.subscriptions[ticker] = {
          'entry': bars[lookback-1]['h'],
          'sl': bars[lookback-1]['l'],
          'tp': self.tickers[ticker].ignition['h']
        }
        self.data.subscribe_to_ticker([ticker])

      # calculate if ignition/pullback should be removed
      diff = diff_minutes(self.tickers[ticker].ignition['t'], curr_bar['t'])
      pb_len = self.tickers[ticker].ignition['h'] - curr_bar['l']
      if (diff > 4):
        log.debug('[{}]Ignition/pullback removed for {}: ignition too old'.format(curr_bar['t'], ticker))
        self.unsubscribe(ticker)
      elif (pb_len/self.tickers[ticker].ignition['dist'] > .75):
        log.debug('[{}]Ignition/pullback removed for {}: pullback too large'.format(curr_bar['t'], ticker))
        log.debug(self.tickers[ticker].ignition['dist'])
        log.debug(pb_len)
        log.debug(self.tickers[ticker].ignition['h'])
        log.debug(curr_bar['l'])
        self.unsubscribe(ticker)