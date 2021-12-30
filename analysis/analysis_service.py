from models.position import PositionStatus, get_positions
from common.utils import date_to_timestamp

import math

class AnalysisService(object):
    def __init__(self):
        return

    def calculate_performance(self, db_instance, strategy, start_time, end_time, starting_balance=None):
        payload = {
            'starting_balance': starting_balance,
            'total_trades': 0,
            'total_winners': 0,
            'total_losers': 0,
            'total_profit': 0,
        }

        filters = {
            'strategy': strategy,
            'status': PositionStatus.CLOSED,
        }
        positions = get_positions(db_instance, filters, start_time, end_time)

        for position in positions:
            payload['total_trades'] += 1

            result = (position.close_price - position.entry_price) * position.quantity
            if result > 0:
                payload['total_winners'] +=1
            else:
                payload['total_losers'] += 1
            payload['total_profit'] += result

        if starting_balance:
            payload['roi'] = payload['total_profit']/payload['starting_balance']
        payload['total_profit'] = math.floor(payload['total_profit'] * 100) / 100

        return payload