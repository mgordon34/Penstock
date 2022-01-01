from abc import abstractmethod

class BaseStrategy(object):

    @abstractmethod
    def handle_mkt_event(self):
        raise NotImplementedError('handle_mkt_event() should be implemented')