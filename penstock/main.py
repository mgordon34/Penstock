from  flask import Flask
import logging
import threading

import common.config as config
from event import *
from portfolio import Portfolio
from stream import HistoricalDataStreamer, LiveDataStreamer, OutofDataError
from ta.strategies import HistoricalThreeBarStrategy, LiveThreeBarStrategy
import queue

log = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

app = Flask(__name__)

events = queue.Queue()
stream = None
strat = None
if config.type == 'historical':
  stream = HistoricalDataStreamer(config.db_file, events, 'bars', config.symbols, '2021-10-25:30:00Z', '2021-10-29:59:00Z')
  strat = HistoricalThreeBarStrategy(events, stream)
elif config.type == 'live':
  stream = LiveDataStreamer(config.db_file, events, config.symbols)
  strat = LiveThreeBarStrategy(events, stream)
  stream.run()
portfolio = Portfolio(events, config.starting_balance, config.pct_buying_power, config.max_positions)


@app.route('/historical')
def historical_run():
    total_profit = 0
    total_winners = 0
    total_losers = 0
    balance = config.starting_balance

    for date in config.dates:
        stream = HistoricalDataStreamer(config.db_file, events, 'bars', config.symbols, date+'T13:30:00Z', date+'T19:59:00Z')
        strat = HistoricalThreeBarStrategy(events, stream)
        portfolio = Portfolio(events, balance, config.pct_buying_power, config.max_positions)
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
                log.info(f'-----------Performance for {date}-----------')
                result = portfolio.calculate_performance()
                log.info(f'--------------------------------------------')
                balance += result['profit']
                total_profit += result['profit']
                total_winners += result['winners']
                total_losers += result['losers']
                break

        log.info(f'===========Performance for week===========')
        log.info(f'Starting balance: ${config.starting_balance:,.2f}')
        log.info('${:,.2f} made in {} trades. {} winners and {} losers'.format(total_profit, total_winners+total_losers, total_winners, total_losers))
        log.info(f'Ending balance: ${config.starting_balance + total_profit:,.2f}')
        log.info('Total ROI: {:.2%}'.format(total_profit/config.starting_balance))
        log.info(f'==========================================')


@app.route('/')
def hello_world():
    log.debug('Handling request for /')
    return '<p>Hello, from stonks api!</p>'

@app.route('/token')
def initialize():
    log.debug('Handling request for /token')


@app.route('/run')
def run():
    total_profit = 0
    total_winners = 0
    total_losers = 0
    balance = config.starting_balance

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

historical_run()
# run_thread = threading.Thread(target=run)
# run_thread.start()
# app.run(host="0.0.0.0", port=6969)