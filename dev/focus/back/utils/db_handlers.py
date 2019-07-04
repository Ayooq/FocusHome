import uuid
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

    conn = sqlite3.connect(filename, check_same_thread=False)
    db_file = open(filename, 'rb')
    db_initiated = db_file.read(1)
    db_file.close()

    if not db_initiated:
        cursor = conn.cursor()

        try:
            _create_schema(cursor)
        except sqlite3.Error:
            conn.rollback()
            raise
        else:
            print('DB initiated.')
            conn.commit()
    else:
        print('The DB file is not empty, skipping the schema creation step.')

    return conn


def _create_schema(cursor):
    _create_config_table(cursor)

    _mapping = {
        'events': (
            'type TEXT',
            ',',
            'message TEXT',
        ),
        'gpio_status': (
            'pin INTEGER',
            ' UNIQUE,',
            'description TEXT, state TEXT',
        ),
        'gpio_status_archive': (
            'pin INTEGER',
            ',',
            'description TEXT, state TEXT',
        ),
    }

    for table, columns in _mapping.items():
        _create_defined_table(cursor, table, columns)


def _create_config_table(cursor):
    cursor.execute(
        '''CREATE TABLE config
                  (device_id TEXT NOT NULL UNIQUE,
                  device_location TEXT,
                  broker_host TEXT NOT NULL,
                  broker_port INTEGER,
                  keep_alive INTEGER NOT NULL CHECK(keep_alive > 3),
                  cpu_min REAL NOT NULL CHECK(cpu_min > -0.1),
                  cpu_max REAL NOT NULL CHECK(cpu_max < 200.1),
                  cpu_threshold REAL NOT NULL,
                  cpu_hysteresis REAL,
                  cpu_timedelta INTEGER NOT NULL,
                  external_min REAL CHECK(external_min > -0.1),
                  external_max REAL CHECK(external_max < 200.1),
                  external_threshold REAL NOT NULL,
                  external_hysteresis REAL,
                  external_timedelta INTEGER NOT NULL);'''
    )


def _create_defined_table(cursor, name, columns):
    col1, col2, col3 = columns
    sql_command = '''CREATE TABLE {}
                            (id INTEGER PRIMARY KEY,
                            timestamp TEXT,
                            {},
                            family TEXT,
                            unit TEXT{}
                            {});'''.format(name, col1, col2, col3)
    print(sql_command)
    cursor.execute(sql_command)


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

    tabledata = (
        device['id'] + str(uuid.uuid4())[:8],
        device['location'],
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
    tables_set = {'config'}

    fill_table(conn, cursor, tables_set, tabledata)

    return conn


def set_initial_gpio_status(conn, units: dict):
    """Записать текущее состояние всех компонентов единого семейства.

    Параметры:
      :param conn: — объект соединения с БД;
      :param units: — кортеж из семейств компонентов устройства.

    Вернуть объект соединения с БД.
    """

    timestamp = datetime.now().isoformat(sep=' ')
    cursor = conn.cursor()
    tables_set = {'gpio_status', 'gpio_status_archive'}

    for family, group in units.items():
        for k, v in group.items():
            if family == 'couts':
                for _ in (v.control, v.socket):
                    tabledata = [timestamp, _.pin, family, _.id,
                                 _.description, _.state]
                    print(tabledata)
                    fill_table(conn, cursor, tables_set, tabledata)
            else:
                tabledata = [timestamp, v.pin, family, k,
                             v.description, v.state]
                print(tabledata)
                fill_table(conn, cursor, tables_set, tabledata)

    return conn


def fill_table(conn, cursor, tables_set: set, tabledata):
    """Заполнить таблицы указанными значениями.

    Параметры:
      :param cursor: — объект указателя БД;
      :param tables_set: — набор наименований целевых таблиц;
      :param tabledata: — упорядоченная коллекция данных для заполнения.
    """

    for tablename in tables_set:
        try:
            cursor.execute(SQL[tablename], tabledata)
        except sqlite3.Error:
            print("Couldn't fill the %s table properly!" % tablename)
            conn.rollback()
        else:
            print("The %s table has been filled with data." % tablename)
            conn.commit()


def get_device_id(conn):
    """Возвратить имя устройства."""

    cursor = conn.cursor()
    cursor.execute('SELECT device_id FROM config;')

    return cursor.fetchone()[0]


def define_broker(conn):
    """Определить адрес хоста и порт, через который будет осуществляться
    обмен данными с посредником, а также допустимое время простоя между
    отправкой сообщений в секундах.

    Параметры:
      :param cursor: — объект указателя БД.

    Вернуть кортеж вида: (адрес, порт, время простоя).
    """

    cursor = conn.cursor()
    cursor.execute(
        'SELECT broker_host, broker_port, keep_alive FROM config;'
    )

    return cursor.fetchall()[0]


GPIO_TABLE_STRUCTURE = {
    'columns': '(timestamp, pin, family, unit, description, state)',
    'values': 'VALUES (?, ?, ?, ?, ?, ?);',
}

SQL = {
    'config': '''REPLACE INTO config
                         (device_id, device_location, broker_host, broker_port,
                         keep_alive, cpu_min, cpu_max, cpu_threshold,
                         cpu_hysteresis, cpu_timedelta, external_min,
                         external_max, external_threshold, external_hysteresis,
                         external_timedelta)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',

    'events': '''INSERT INTO events
                        (timestamp, type, family, unit, message)
                 VALUES (?, ?, ?, ?, ?);''',

    'gpio_status': 'REPLACE INTO gpio_status {} {}'.format(
        GPIO_TABLE_STRUCTURE['columns'], GPIO_TABLE_STRUCTURE['values']
    ),

    'gpio_status_archive': 'INSERT INTO gpio_status_archive {} {}'.format(
        GPIO_TABLE_STRUCTURE['columns'], GPIO_TABLE_STRUCTURE['values']
    ),
}
