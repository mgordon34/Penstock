import yfinance as yf
from datetime import datetime, timedelta

import logging
log = logging.getLogger(__name__)

def get_last_close(symbol):
  data = yf.Ticker(symbol)
  today = datetime.now().date()
  yesterday = today - timedelta(days=1)
  df = data.history(period='1d', start=yesterday.strftime('%Y-%m-%d'), end=today.strftime('%Y-%m-%d'))
  return df.loc[yesterday.strftime('%Y-%m-%d')].Close

if __name__ == '__main__':

  log_level = logging.DEBUG
  log_format = '%(asctime)s.%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
  logging.basicConfig(level=log_level, format=log_format, datefmt='%Y-%m-%d:%H:%M:%S')
  get_last_close('TSLA')