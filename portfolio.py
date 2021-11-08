import common.config as config
from event import SignalEvent

import logging
log = logging.getLogger(__name__)

class TradeObject(object):
  def __init__(self, symbol, shares, entry, sl, tp, start):
    self.symbol = symbol
    self.shares = shares
    self.entry = entry
    self.sl = sl
    self.tp = tp
    self.start_time = start
    self.end_time = None
    self.result = False

class Portfolio(object):
  def __init__(self, events, balance, pct_bp, max_positions):
    self.events = events
    self.starting_balance = balance
    self.balance = balance
    self.pct_bp = pct_bp
    self.max_positions = max_positions
    self.positions = []
    self.trade_hist = []

  def handle_signal_event(self, event):
    symbol = event.symbol

    if event.signal_type == 'BUY':
      if len(self.positions) >= self.max_positions:
        logging.debug('Max positions reached, not buying {}'.format(event.symbol))
        return
      if self.has_position(event.symbol):
        logging.debug('Position already open for {}, not buying'.format(event.symbol))
        return
      num_shares = self.calculate_shares(event.price)
      new_pos = TradeObject(event.symbol, num_shares, event.price, event.sl, event.tp, event.timestamp)
      self.positions.append(new_pos)
      logging.debug('Entered position: {} shares of {} at {}'.format(num_shares, event.symbol, event.price))

    if event.signal_type == 'CLOSE':
      pos = self.remove_position(event.symbol, event.price, event.timestamp)
      if pos:
        logging.debug('Closing position for {} at {}'.format(event.symbol, event.price))
      else:
        logging.debug('No position open for {}, no need to close'.format(event.symbol))

  def calculate_performance(self):
    profit = 0
    winners = 0
    losers = 0
    for trade in self.trade_hist:
      trade_p = trade.result
      if trade_p >= 0:
        winners += 1
      else:
        logging.info('{} - bought at {}, stopped out at {}'.format(trade.symbol, trade.entry, trade.sl))
        losers += 1
      profit += trade_p * trade.shares

    logging.info('${:,.2f} made in {} trades. {} winners and {} losers'.format(profit, winners+losers, winners, losers))
    logging.info('Total ROI: {:.2%}'.format(profit/self.starting_balance))
    return {
      'profit': profit,
      'winners': winners,
      'losers': losers
    }

  # Helper function to determine if portfolio already has a position in specified symbol
  def has_position(self, symbol):
    for i in self.positions:
      if i.symbol == symbol:
        return True
    return False

  # Helper function to remove a position from active positions, will return None if no 
  # position for specified symbol is present
  def remove_position(self, symbol, price, timestamp):
    for i in range(0, len(self.positions)):
      if self.positions[i].symbol == symbol:
        position = self.positions.pop(i)
        position.result = price - position.entry
        position.end_time = timestamp
        self.trade_hist.append(position)
        return position
    return None

  # Helper function to determine how many shares can be bought based on buying power
  # and rules for pct_buying_power
  def calculate_shares(self, price):
    return (self.balance * self.pct_bp) // price



if __name__ == '__main__': 
  port = Portfolio(None, 1000, .9, 1)
  port.handle_signal_event(SignalEvent('SPY', 'BUY', 69))
  port.handle_signal_event(SignalEvent('SPY', 'BUY', 69))
  port.handle_signal_event(SignalEvent('SPY', 'CLOSE', 72))
  port.handle_signal_event(SignalEvent('SPY', 'CLOSE', 72))
  port.handle_signal_event(SignalEvent('SPY', 'BUY', 69))
  port.handle_signal_event(SignalEvent('SPY', 'CLOSE', 72))
  port.calculate_performance()

