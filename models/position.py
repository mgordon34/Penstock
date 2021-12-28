from strenum import StrEnum

class PositionStatus(StrEnum):
    OPEN = 'OPEN',
    WIN = 'WIN',
    LOSS = 'LOSS'

class Position(object):
    
    def __init__(self, db_instance, symbol, type, quantity, price, tp, sl, strategy,
                 start_time, end_time=None, status=None, id=None, skip_insert=False):
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

        if skip_insert:
            if not id:
                raise Exception('ID needed if skip_insert is active')
            self.id = id
        else:
            self.id = self.insert(db_instance)
    
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
        return db_instance.insert_model(sql, self.get_position_object())

    def save(self, db_instance, fields_changed):
        sql = f'''UPDATE positions SET '''
        sql += ', '.join([
            add_filter(field_name, getattr(self, field_name))
            for field_name in fields_changed
        ])
        sql += f' where id={self.id}'
        print(sql)
        return db_instance.update_model(sql)

def get_open_positions(db_instance, filters=None):
    sql = f'''SELECT * FROM positions'''
    if filters:
        sql += ''' WHERE '''
        sql += ''' AND '''.join([
            add_filter(filter_name, filters[filter_name]) for filter_name in filters
        ])

    cur = db_instance.conn.cursor()
    print(f'get sql: {sql}')
    cur.execute(sql)
    return cur.fetchall()

def add_filter(filter_name, filter_value):
    if isinstance(filter_value, StrEnum):
        filter_value = filter_value.value
    if type(filter_value == str):
        filter_value = f"'{filter_value}'"
    return f'{filter_name}={filter_value}'