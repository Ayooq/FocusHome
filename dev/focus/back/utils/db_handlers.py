import sqlite3
from sqlite3 import Error
from datetime import datetime


def init_db(filename: str):
    """Инициализировать БД SQLite3 в файле с именем :param filename:.

    Создать схему с таблицами:
    1) config — локальная конфигурация устройства;
    2) events — все зарегистрированные события;
    3) gpio_status — текущее состояние компонентов устройства;
    4) gpio_status_archive — история состояний компонентов за всё время.

    Схема создаётся единожды при самом первом запуске устройства.
    Это обеспечивается проверкой наличия указанных таблиц в БД путём
    соответствующих SQL-запросов.

    Возвратить объект соединения с БД, в противном случае вывести сообщение об
    ошибке.
    """

    conn = sqlite3.connect(filename)
    cursor = conn.cursor()

    try:
        _create_schema(cursor)
    except:
        pass

    cursor.close()

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
        '''CREATE TABLE IF NOT EXISTS config
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
        '''CREATE TABLE IF NOT EXISTS {0}
                  (id INTEGER PRIMARY KEY,
                  timestamp TEXT,
                  {1},
                  family TEXT,
                  unit TEXT,
                  {2});'''.format(name, col1, col2)
    )


def set_initial_gpio_status(cursor, family):
    """Записать текущее состояние всех компонентов единого семейства.

    Параметры:
      :param cursor: — объект указателя БД;
      :param family: — название семейства компонентов.
    """

    timestamp = datetime.now().isoformat(sep=' ')

    try:
        for unit in family.values():
            for gpio in unit.values():
                if isinstance(gpio, dict):
                    for complect in gpio.values():
                        tabledata = [timestamp, complect.pin, family,
                                     complect.id, complect.description,
                                     complect.state]
                        cursor.execute(SQL['gpio_status_init'], tabledata)

                else:
                    tabledata = [timestamp, gpio.pin, family, gpio.id,
                                 gpio.description, gpio.state]
                    cursor.execute(SQL['gpio_status_init'], tabledata)
    except sqlite3.IntegrityError:
        pass


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

    return fill_table(conn, 'config', data)


def fill_table(conn, tablename, tabledata):
    """Заполнить таблицу указанными значениями.

    Параметры:
      :param conn: — объект соединения с БД;
      :param tablename: — название целевой таблицы;
      :param tabledata: — упорядоченная коллекция данных для заполнения.

    Вернуть объект соединения с БД.
    """
    cursor = conn.cursor()
    cursor.execute(SQL[tablename], tabledata)
    cursor.close()

    return conn


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
