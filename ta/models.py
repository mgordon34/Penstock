
class Bar(object):
    def __init__(self, _open, high, low, close):
        self.open = _open
        self.high = high,
        self.low = low,
        self.close = close,

class DailyData(object):
    def __init__(self):
        self.ignition = False
        self.pullback = False
        self.hod = None
        self.lod = None