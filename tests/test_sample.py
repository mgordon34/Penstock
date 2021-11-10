import pytest
import queue

import common.config as config
from event import *
from db import DB
from portfolio import Portfolio
from stream import HistoricalDataStreamer, OutofDataError
from ta.strategies import HistoricalThreeBarStrategy
import tests.utils as utils


class TestSample:
  db = None

  @classmethod
  def setup_class(cls):
    db_file = utils.setup_test_db()
    TestSample.db = DB(db_file)

  @classmethod
  def teardown_class(cls):
    utils.teardown_test_db()

  def test_answer(self):
    assert 3 == 3

  def test_end_to_end(self):
    events = queue.Queue()
    stream = HistoricalDataStreamer(events, 'bars', config.symbols, '2021-08-12T13:30:00Z', '2021-08-12T19:59:00Z')
    strat = HistoricalThreeBarStrategy(events, stream)
    portfolio = Portfolio(events, 30000, 3*.9, 1)

    total_profit = 0
    total_winners = 0 
    total_losers = 0
    balance = 30000

    symbols = ['SPY', 'AAPL', 'MSFT', 'TSLA', 'PLUG', 'WKHS', 'BIDU', 'ROKU', 'AMD', 'NVDA',
    'TWTR', 'FB', 'NFLX', 'CRSR', 'AMC', 'GME', 'RBLX', 'ATVI', 'BYND', 'JBLU', 'DAL', 'CCL', 
    'SNOW', 'SHOP', 'TLRY', 'MRNA', 'PFE', 'DFS', 'WFC', 'JPM', 'RKT', 'WMT', 'F', 'V', 'IYE', 
    'XOM']
    dates = ['2021-10-25', '2021-10-26', '2021-10-27', '2021-10-28', '2021-10-29']

    for date in dates:
      stream = HistoricalDataStreamer(events, 'bars', symbols, date+'T13:30:00Z', date+'T19:59:00Z')
      strat = HistoricalThreeBarStrategy(events, stream)
      portfolio = Portfolio(events, balance, 3*.9, 1)

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
          result = portfolio.calculate_performance()
          balance += result['profit']
          total_profit += result['profit']
          total_winners += result['winners']
          total_losers += result['losers']
          break
    print('Profit: ${:,.2f}, {} winners and {} losers'.format(total_profit, total_winners, total_losers))
    assert total_profit == 10357.731
    assert total_winners == 101
    assert total_losers == 74