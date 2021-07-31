class Event(object):
    """
    Base class
    """

    pass

class MarketEvent(Event):
    """
    Handles tick/candle data
    """

    def __init__(self, mkt_type):
        self.type = 'MARKET'
        self.mkt_type = mkt_type

class SignalEvent(Event):
    """
    Handles the event of a strategy generating a signal
    """
    
    def __init__(self, symbol, datetime, signal_type):
        self.type = 'SIGNAL'
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type

class OrderEvent(Event):
    """
    Handles the event of sending an order to brokerage
    """

    def __init__(self, symbol, order_type, quantity, direction):
        self.type = 'ORDER'
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction

    def print_order(self):
        print('Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s') % (self.symbol, self.order_type, self.quantity, self.direction)

class FillEvent(Event):
    """
    Handles the event of a fill confirmation from brokerage
    """

    def __init__(self, timeindex, symbol, exchange, quantity, 
                 direction, fill_cost, commission=None):
        self.type = 'FILL'
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost