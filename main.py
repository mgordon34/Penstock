from stream import HistoricalDataStreamer, LiveDataStreamer, OutofDataError
from strategy import ThreeBarStrategy
from portfolio import Portfolio
import queue
from event import *
import config

events = queue.Queue()
# stream = LiveDataStreamer(events)
stream = HistoricalDataStreamer(events, 'bars', config.tickers, '2021-08-12T13:30:00Z', '2021-08-12T19:59:00Z')
strat = ThreeBarStrategy(events, stream)
portfolio = Portfolio(events, config.starting_balance, config.pct_buying_power, config.max_positions)

# stream.run()

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
    print('Streamer ran out of bars, finishing...')
    portfolio.calculate_performance()
    quit()
