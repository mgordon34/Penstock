from abc import abstractmethod

from common.models import BarObject

class BaseStrategy(object):

    @abstractmethod
    def handle_mkt_event(self):
        raise NotImplementedError('handle_mkt_event() should be implemented')