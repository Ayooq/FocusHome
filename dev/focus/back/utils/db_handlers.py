import sqlite3
from sqlite3 import Error


def _create_schema(cursor):
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS config
                  (device TEXT NOT NULL UNIQUE,
                  broker_host TEXT NOT NULL,
                  broker_port INTEGER,
                  keepalive INTEGER NOT NULL CHECK(keepalive > 3),
                  cpu_min REAL NOT NULL CHECK(cpu_min > 0.1),
                  cpu_max REAL NOT NULL CHECK(cpu_max < 199.9),
                  cpu_threshold REAL NOT NULL,
                  cpu_hysteresis REAL,
                  cpu_timedelta REAL NOT NULL CHECK(cpu_timedelta >= 10),
                  board_min REAL CHECK(board_min > 0),
                  board_max REAL CHECK(board_max < 200),
                  board_threshold REAL NOT NULL,
                  board_hysteresis REAL,
                  board_timedelta REAL NOT NULL CHECK(board_timedelta >= 10));
                  
           CREATE TABLE IF NOT EXISTS events
                  (id INTEGER PRIMARY KEY,
                  timestamp TEXT,
                  type TEXT,
                  device TEXT,
                  group TEXT,
                  unit TEXT,
                  msg TEXT);
                  
           CREATE TABLE IF NOT EXISTS gpio_status
                  (id INTEGER PRIMARY KEY,
                  timestamp TEXT,
                  device TEXT,
                  pin INTEGER UNIQUE,
                  group TEXT,
                  internal_name TEXT,
                  verbose_name TEXT,
                  state TEXT);

           CREATE TABLE IF NOT EXISTS gpio_status_archive
                  (id INTEGER PRIMARY KEY,
                  timestamp TEXT,
                  device TEXT,
                  pin INTEGER,
                  group TEXT,
                  internal_name TEXT,
                  verbose_name TEXT,
                  state TEXT);'''
    )


def init_db(filename):
    """Инициализировать БД SQLite3 с именем :str filename:.

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

    try:
        conn = sqlite3.connect(filename)
        print(sqlite3.version)

        cursor = conn.cursor()
        _create_schema(cursor)
        cursor.close()
    except Error as e:
        print('Ошибка в настройке базы данных!', e, sep='\n\n')
    else:
        return conn


def set_config(conn, config):
    """Загрузить настройки по умолчанию в таблицу конфигурации.

    Параметры:
        :object conn: — объект соединения с БД;
        :dict config: — словарь конфигурации оборудования.

    Вернуть объект соединения с БД.
    """

    device = config['device']
    broker = device['broker']
    temperature = device['temp']
    cpu = temperature['cpu']
    board = temperature['bnk']

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
        board['min'],
        board['max'],
        board['threshold'],
        board['hysteresis'],
        board['timedelta'],
    )

    return fill_table(conn, 'config', data)


def fill_table(conn, tablename, data):
    """Заполнить таблицу указанными значениями.

    Параметры:
        :object conn: — объект соединения с БД;
        :str tablename: — название целевой таблицы;
        :list, tuple data: — упорядоченная коллекция данных для заполнения.

    Вернуть объект соединения с БД.
    """
    cursor = conn.cursor()
    cursor.execute(_SQL[tablename], data)
    cursor.close()

    return conn


_SQL = {
    'config': '''INSERT INTO config
                        (device, keepalive, broker_host, broker_port,
                        cpu_min, cpu_max, cpu_threshold, cpu_hysteresis,
                        cpu_timedelta, board_min, board_max,
                        board_threshold, board_hysteresis, board_timedelta)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',

    'events': '''INSERT INTO events(timestamp, type, device, group, unit, msg)
                 VALUES (?, ?, ?, ?, ?, ?);''',

    'gpio_status': '''REPLACE INTO gpio_status
                              (timestamp, device, pin, group,
                              internal_name, verbose_name, state)
                       VALUES (?, ?, ?, ?, ?, ?, ?);''',

    'gpio_status_archive': '''INSERT INTO gpio_status_archive
                                     (timestamp, device, pin, group,
                                     internal_name, verbose_name, state)
                              VALUES (?, ?, ?, ?, ?, ?, ?);''',
}
