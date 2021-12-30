from strenum import StrEnum

class TimeOptions(StrEnum):
    START = '00:00:00'
    OPEN = '13:30:00',
    CLOSE = '19:59:59',
    END = '23:59:59'

def date_to_timestamp(date, specifier):
    return f'{date}T{specifier.value}Z'