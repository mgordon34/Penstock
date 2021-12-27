from enum import Enum

class PositionStatus(Enum):
    OPEN = 'OPEN',
    WIN = 'WIN',
    LOSS = 'LOSS'

class Position(object):
    
    def __init__(self, db_instance, symbol, type, quantity, price, tp, sl, strategy,
                 start_time, end_time=None, status=None):
        self.symbol = symbol
        self.type = type
        self.quantity = quantity
        self.price = price
        self.tp = tp
        self.sl = sl
        self.strategy = strategy
        self.start_time = start_time
        self.end_time = end_time
        self.status = status if status else PositionStatus.OPEN
        self.insert_position(db_instance)

    def insert_position(self, db_instance):
        position_sql = '''INSERT INTO positions(symbol, quantity, opening_price,
            take_profit, stop_loss, strategy, status, start_time, end_time)
            VALUES(?,?,?,?,?,?,?,?,?)'''
        position_id = db_instance.insert_model(position_sql, self.get_position_object())
        self.position_id = position_id
        return position_id
    
    def get_position_object(self):
        return (
            self.symbol,
            self.quantity,
            self.price,
            self.tp,
            self.sl,
            self.strategy,
            self.status,
            self.start_time,
            self.end_time
        )