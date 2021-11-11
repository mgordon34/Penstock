from datetime import datetime


class Analyzer(object):

    @classmethod
    def diff_minutes(self, old, new):
        if not old:
            return -1
        old = datetime.strptime(old, "%Y-%m-%dT%H:%M:%SZ")
        new = datetime.strptime(new, "%Y-%m-%dT%H:%M:%SZ")
        ret = abs((old-new).total_seconds()/60)
        return ret

    @classmethod
    def find_lowest(self, bars):
        if not bars:
            return (None, None)

        low = (float('+inf'), None)
        for bar in bars:
            if bar['l'] < low[0]:
                low = (bar['l'], bar['t'])
        return low