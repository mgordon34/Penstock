from strenum import StrEnum

class PositionStatus(StrEnum):
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
        self.take_profit = tp
        self.stop_loss = sl
        self.strategy = strategy
        self.start_time = start_time
        self.end_time = end_time
        self.status = status if status else PositionStatus.OPEN
        self.insert(db_instance)
    
    def get_position_object(self):
        return (
            self.symbol,
            self.quantity,
            self.price,
            self.take_profit,
            self.stop_loss,
            self.strategy,
            self.status.value,
            self.start_time,
            self.end_time
        )

    def insert(self, db_instance):
        sql = '''INSERT INTO positions(symbol, quantity, opening_price,
            take_profit, stop_loss, strategy, status, start_time, end_time)
            VALUES(?,?,?,?,?,?,?,?,?)'''
        id = db_instance.insert_model(sql, self.get_position_object())
        self.id = id
        return id

    def save(self, db_instance, fields_changed):
        sql = f'''UPDATE positions SET '''
        sql += ', '.join(
            [self.add_set_statement(field_name) for field_name in fields_changed]
        )
        sql += f' where id={self.id}'
        return db_instance.update_model(sql)

    def add_set_statement(self, field_name):
        field_value = getattr(self, field_name)
        if isinstance(field_value, StrEnum):
            field_value = field_value.value
        if type(field_value) == str:
            field_value = f"'{field_value}'"
        return f'{field_name}={field_value}'