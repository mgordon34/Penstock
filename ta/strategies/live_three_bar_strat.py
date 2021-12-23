from collections import defaultdict
from datetime import datetime
import logging

import common.config as config
from event import SignalEvent
from ta.analyzer import Analyzer
from ta.models import DailyData
from ta.strategies import BaseStrategy

log = logging.getLogger(__name__)

class LiveThreeBarStrategy(BaseStrategy):
  def __init__(self, events, data):
    self.subscriptions = {}
    self.tickers = defaultdict(DailyData)
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
      for symbol in list(self.subscriptions):
        if self.subscriptions[symbol] and self.data.get_price(symbol):
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
      log.debug(f'{symbol} tp: {self.positions[symbol]["tp"]}')
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
    diff = Analyzer.diff_minutes(self.tickers[ticker].hod[1], curr_bar['t'])
    if diff == 0:
      log.debug('new high for {}: {}'.format(ticker, curr_bar))
      qual = True
      for i in range(len(bars)-3, len(bars)):
        if bars[i]['h'] < bars[i-1]['h']:
          qual = False
      if qual:
        log.debug('[{}]Ignition activated for {}'.format(curr_bar['t'], ticker))
        dist = curr_bar['h'] - Analyzer.find_lowest(bars)[0]
        if dist > 0:
          self.tickers[ticker].ignition = {'h': curr_bar['h'], 't': curr_bar['t'], 'dist': dist}
          self.tickers[ticker].pullback = False
    
    if self.tickers[ticker].ignition and Analyzer.diff_minutes(self.tickers[ticker].ignition['t'], curr_bar['t']) > 0:
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
      diff = Analyzer.diff_minutes(self.tickers[ticker].ignition['t'], curr_bar['t'])
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