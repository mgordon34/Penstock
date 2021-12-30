from strenum import StrEnum

class PositionStatus(StrEnum):
    OPEN = 'OPEN',
    CLOSED = 'CLOSED'

class Position(object):
    
    def __init__(self, db_instance, symbol, type, quantity, price, tp, sl, strategy,
                 start_time, end_time=None, close_price=None, status=None, id=None):
        self.symbol = symbol
        self.type = type
        self.quantity = quantity
        self.entry_price = price
        self.take_profit = tp
        self.stop_loss = sl
        self.strategy = strategy
        self.start_time = start_time
        self.end_time = end_time
        self.close_price = close_price
        self.status = status if status else PositionStatus.OPEN

        if not db_instance:
            if not id:
                raise Exception('ID needed if no db_instance is provided')
            self.id = id
        else:
            self.id = self.insert(db_instance)
    
    def get_position_object(self):
        return (
            self.symbol,
            self.type,
            self.quantity,
            self.entry_price,
            self.take_profit,
            self.stop_loss,
            self.strategy,
            self.start_time,
            self.end_time,
            self.close_price,
            self.status.value,
        )

    def insert(self, db_instance):
        sql = '''INSERT INTO positions(symbol, type, quantity, entry_price,
            take_profit, stop_loss, strategy, start_time, end_time, close_price,
            status)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)'''
        return db_instance.insert_model(sql, self.get_position_object())

    def save(self, db_instance, fields_changed):
        sql = f'''UPDATE positions SET '''
        sql += ', '.join([
            add_filter(field_name, getattr(self, field_name))
            for field_name in fields_changed
        ])
        sql += f' where id={self.id}'
        return db_instance.update_model(sql)

def get_positions(db_instance, filters=None, start_time=None, end_time=None):
    where_used = False
    sql = f'''SELECT * FROM positions'''
    if filters:
        sql += ''' WHERE '''
        sql += ''' AND '''.join([
            add_filter(filter_name, filters[filter_name]) for filter_name in filters
        ])
        where_used = True
    if start_time and end_time:
        sql += ''' AND ''' if where_used else ''' WHERE '''
        sql += f'''datetime(start_time) BETWEEN datetime('{start_time}') AND datetime('{end_time}')'''
    sql +=  ''' ORDER BY datetime(start_time)'''

    cur = db_instance.conn.cursor()
    cur.execute(sql)
    return [create_position_object(res) for res in cur.fetchall()]

def add_filter(filter_name, filter_value):
    if isinstance(filter_value, StrEnum):
        filter_value = filter_value.value
    if type(filter_value == str):
        filter_value = f"'{filter_value}'"
    return f'{filter_name}={filter_value}'

def create_position_object(db_tuple):
    return Position(None, *db_tuple[1:], db_tuple[0])