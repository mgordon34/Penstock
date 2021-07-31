from stream import HistoricalDataStreamer, LiveDataStreamer, OutofDataError
from strategy import ThreeBarStrategy
import queue
from event import *
import config

events = queue.Queue()
# stream = LiveDataStreamer(events)
stream = HistoricalDataStreamer(events, 'bars', config.tickers, '2021-07-12T13:30:00Z', '2021-07-12T19:59:00Z')
strat = ThreeBarStrategy(events, stream)

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
  except OutofDataError:
    print('Streamer ran out of bars, finishing...')
    quit()
