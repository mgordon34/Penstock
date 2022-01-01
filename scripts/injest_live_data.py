import logging
from logging.handlers import RotatingFileHandler
import queue
from time import sleep

from stream import LiveDataStreamer
from event import *
import common.config as config

log = logging.getLogger(__name__)
handler = RotatingFileHandler(config.injest_logging_path, maxBytes=20000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

def injest_live_data(db_file_name):
    events = queue.Queue()
    stream = LiveDataStreamer(db_file_name, events, config.backtest_symbols, config.backtest_symbols)
    stream.run()

    conn_timeout = 5
    while not stream.ws.sock.connected and conn_timeout:
        sleep(1)
        conn_timeout -= 1

    msg_counter = 0
    while stream.ws.sock.connected:
        sleep(1)
        stream.update_price()


if __name__ == "__main__":
    injest_live_data('trades_archive.db')
