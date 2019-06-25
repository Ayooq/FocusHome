import sqlite3
from datetime import datetime


def init_db(filename: str):
    """Инициализировать БД SQLite3 в файле с именем :param filename:.

    Создать схему с таблицами:
    1) config — локальная конфигурация устройства;
    2) events — все зарегистрированные события;
    3) gpio_status — текущее состояние компонентов устройства;
    4) gpio_status_archive — история состояний компонентов за всё время.

    Схема создаётся единожды при самом первом запуске устройства.
    Это обеспечивается проверкой наличия непустых строк в указанном файле.

    Возвратить объект соединения с БД.
    """

    conn = sqlite3.connect(filename)
    db_file = open(filename, 'rb')
    db_initiated = db_file.read(1)
    db_file.close()

    if not db_initiated:
        cursor = conn.cursor()

        try:
            _create_schema(cursor)
            cursor.close()
        except sqlite3.Error:
            conn.rollback()
        else:
            conn.commit()

    return conn


def _create_schema(cursor):
    _create_config_table(cursor)

    gpio_columns = (
        'pin INTEGER UNIQUE',
        'description TEXT, state TEXT',
    )
    tables = {
        'events': ('type TEXT', 'message TEXT'),
        'gpio_status': gpio_columns,
        'gpio_status_archive': gpio_columns,
    }

    for table, columns in tables.items():
        _create_defined_table(cursor, table, columns)


def _create_config_table(cursor):
    cursor.execute(
        '''CREATE TABLE config
                  (device_id TEXT NOT NULL UNIQUE,
                  broker_host TEXT NOT NULL,
                  broker_port INTEGER,
                  keep_alive INTEGER NOT NULL CHECK(keep_alive > 3),
                  cpu_min REAL NOT NULL CHECK(cpu_min > 0.1),
                  cpu_max REAL NOT NULL CHECK(cpu_max < 199.9),
                  cpu_threshold REAL NOT NULL,
                  cpu_hysteresis REAL,
                  cpu_timedelta INTEGER NOT NULL,
                  external_min REAL CHECK(external_min > 0.1),
                  external_max REAL CHECK(external_max < 199.9),
                  external_threshold REAL NOT NULL,
                  external_hysteresis REAL,
                  external_timedelta INTEGER NOT NULL);'''
    )


def _create_defined_table(cursor, name, columns):
    col1, col2 = columns
    cursor.execute(
        '''CREATE TABLE %s
                  (id INTEGER PRIMARY KEY,
                  timestamp TEXT,
                  ?,
                  family TEXT,
                  unit TEXT,
                  ?);''' % name,
        (col1, col2)
    )


def set_initial_gpio_status(conn, units: dict):
    """Записать текущее состояние всех компонентов единого семейства.

    Параметры:
      :param conn: — объект соединения с БД;
      :param units: — словарь GPIO-компонентов, распределённых по группам.
    """

    cursor = conn.cursor()
    timestamp = datetime.now().isoformat(sep=' ')

    try:
        for family, group in units.items():
            for unit in group:
                if unit.startswith('cmp'):
                    for _ in (group[unit].control, group[unit].socket):
                        tabledata = [timestamp, _.pin, family, _.id,
                                     _.description, _.state]
                        cursor.execute(SQL['gpio_status_init'], tabledata)
                else:
                    tabledata = [timestamp, group[unit].pin, family,
                                 group[unit].id, group[unit].description,
                                 group[unit].state]
                    cursor.execute(SQL['gpio_status_init'], tabledata)

        cursor.close()
    except sqlite3.Error:
        conn.rollback()
    else:
        conn.commit()


def set_config(conn, config: dict):
    """Загрузить настройки по умолчанию в таблицу конфигурации.

    Параметры:
      :param conn: — объект соединения с БД;
      :param config: — конфигурация оборудования в виде словаря.

    Вернуть объект соединения с БД.
    """

    device = config['device']
    broker = device['broker']
    temperature = config['units']['temp']
    cpu = temperature['cpu']
    external = temperature['ext']

    data = (
        device['id'],
        broker['host'],
        broker['port'],
        broker['keepalive'],
        cpu['min'],
        cpu['max'],
        cpu['threshold'],
        cpu['hysteresis'],
        cpu['timedelta'],
        external['min'],
        external['max'],
        external['threshold'],
        external['hysteresis'],
        external['timedelta'],
    )

    cursor = conn.cursor()

    try:
        fill_table(cursor, 'config', data)
        cursor.close()
    except sqlite3.Error:
        conn.rollback()
    else:
        conn.commit()

    return conn


def fill_table(cursor, tablename, tabledata):
    """Заполнить таблицу указанными значениями.

    Параметры:
      :param cursor: — объект указателя БД;
      :param tablename: — название целевой таблицы;
      :param tabledata: — упорядоченная коллекция данных для заполнения.
    """

    cursor.execute(SQL[tablename], tabledata)


GPIO_TABLE_STRUCTURE = {
    'columns': '(timestamp, pin, family, unit, description, state)',
    'values': 'VALUES (?, ?, ?, ?, ?, ?);',
}

SQL = {
    'config': '''INSERT INTO config
                        (device_id, broker_host, broker_port, keep_alive,
                        cpu_min, cpu_max, cpu_threshold, cpu_hysteresis,
                        cpu_timedelta, external_min, external_max,
                        external_threshold, external_hysteresis,
                        external_timedelta)

                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',

    'events': '''INSERT INTO events
                        (timestamp, type, family, unit, message)
                 VALUES (?, ?, ?, ?, ?);''',

    'gpio_status_init': 'INSERT INTO gpio_status {} {}'.format(
        GPIO_TABLE_STRUCTURE['columns'], GPIO_TABLE_STRUCTURE['values']
    ),

    'gpio_status': 'REPLACE INTO gpio_status {} {}'.format(
        GPIO_TABLE_STRUCTURE['columns'], GPIO_TABLE_STRUCTURE['values']
    ),

    'gpio_status_archive': 'INSERT INTO gpio_status_archive {} {}'.format(
        GPIO_TABLE_STRUCTURE['columns'], GPIO_TABLE_STRUCTURE['values']
    ),
}
