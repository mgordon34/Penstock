import logging
import config

class MyLogger(object):
  def __init__(self):
    logging.basicConfig(level=config.log_level)

  def debug(self, message):
    logging.debug(message)

  def info(self, message):
    logging.info(message)

  def error(self, message):
    logging.error(message)

log = MyLogger()