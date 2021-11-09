from stream import HistoricalDataStreamer, LiveDataStreamer, OutofDataError
from strategy import ThreeBarStrategy, LiveThreeBarStrategy
from portfolio import Portfolio
import queue
from event import *
import common.config as config

import logging
log = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

events = queue.Queue()
stream = None
strat = None
if config.type == 'historical':
  stream = HistoricalDataStreamer(events, 'bars', config.symbols, '2021-10-25:30:00Z', '2021-10-29:59:00Z')
  strat = ThreeBarStrategy(events, stream)
elif config.type == 'live':
  stream = LiveDataStreamer(events)
  strat = LiveThreeBarStrategy(events, stream)
  stream.run()
portfolio = Portfolio(events, config.starting_balance, config.pct_buying_power, config.max_positions)

total_profit = 0
total_winners = 0 
total_losers = 0
balance = config.starting_balance

# for date in config.dates:
#   stream = HistoricalDataStreamer(events, 'bars', config.symbols, date+'T13:30:00Z', date+'T19:59:00Z')
#   strat = ThreeBarStrategy(events, stream)
#   portfolio = Portfolio(events, balance, config.pct_buying_power, config.max_positions)

while True:
    try:
        stream.update_price()
        while True:
            try:
                event = events.get(False)
            except queue.Empty:
                break
            else:
                if event.type == 'MARKET':
                    strat.handle_mkt_event(event)
                elif event.type == 'SIGNAL':
                    portfolio.handle_signal_event(event)
    except OutofDataError:
      log.info('Streamer ran out of bars, finishing...')
      result = portfolio.calculate_performance()
      balance += result['profit']
      total_profit += result['profit']
      total_winners += result['winners']
      total_losers += result['losers']
      break

log.info('Profit: ${:,.2f}, {} winners and {} losers'.format(total_profit, total_winners, total_losers))
quit()
