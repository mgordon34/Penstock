from datetime import datetime

from ta.analyzer import Analyzer

class TestAnalyzer:

    def test_diff_minutes_with_neg_result(self):
        old_date = "2021-03-31T01:15:10Z"
        new_date = "2021-03-31T01:16:00Z"
        ret = Analyzer.diff_minutes(old_date, new_date)

        assert ret == 0.8333333333333334

    def test_diff_minutes_with_pos_result(self):
        old_date = "2021-03-31T01:16:00Z"
        new_date = "2021-03-31T01:15:10Z"
        ret = Analyzer.diff_minutes(old_date, new_date)

        assert ret == 0.8333333333333334

    def test_find_lowest(self):
        bars = [
            {'l': 100, 't': '1'},
            {'l': 69, 't': '2'},
            {'l': 420, 't': '3'},
        ]
        (low, time) = Analyzer.find_lowest(bars)

        assert low == 69
        assert time == '2'

    def test_find_lowest_with_empty_returns_nones(self):
        bars = []
        (low, time) = Analyzer.find_lowest(bars)

        assert low == None
        assert time == None