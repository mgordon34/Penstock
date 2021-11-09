from datetime import datetime

class DailyData(object):
    def __init__(self):
        self.ignition = False
        self.pullback = False
        self.hod = None
        self.lod = None


def diff_minutes(old, new):
    if not old:
        return -1
    old = datetime.strptime(old, "%Y-%m-%dT%H:%M:%SZ")
    new = datetime.strptime(new, "%Y-%m-%dT%H:%M:%SZ")
    ret = abs((old-new).total_seconds()/60)
    return ret

def find_lowest(bars):
    low = (float('+inf'), None)
    for bar in bars:
        if bar['l'] < low[0]:
            low = (bar['l'], bar['t'])
    return low