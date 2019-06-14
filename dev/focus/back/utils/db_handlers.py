import sqlite3
from sqlite3 import Error
from datetime import datetime


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


def _create_schema(cursor):
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
                  cpu_timedelta REAL NOT NULL,
                  external_min REAL CHECK(external_min > 0),
                  external_max REAL CHECK(external_max < 200),
                  external_threshold REAL NOT NULL,
                  external_hysteresis REAL,
                  external_timedelta REAL NOT NULL);
                  
           CREATE TABLE IF NOT EXISTS events
                  (id INTEGER PRIMARY KEY,
                  timestamp TEXT,
                  type TEXT,
                  family TEXT,
                  unit TEXT,
                  message TEXT);
                  
           CREATE TABLE IF NOT EXISTS gpio_status
                  (id INTEGER PRIMARY KEY,
                  timestamp TEXT,
                  pin INTEGER UNIQUE,
                  family TEXT,
                  internal_name TEXT,
                  verbose_name TEXT,
                  state TEXT);

           CREATE TABLE IF NOT EXISTS gpio_status_archive
                  (id INTEGER PRIMARY KEY,
                  timestamp TEXT,
                  pin INTEGER UNIQUE,
                  family TEXT,
                  internal_name TEXT,
                  verbose_name TEXT,
                  state TEXT);'''
    )


def set_config(conn, config):
    """Загрузить настройки по умолчанию в таблицу конфигурации.

    Параметры:
        :param conn: — объект соединения с БД;
        :param config: — словарь конфигурации оборудования.

    Вернуть объект соединения с БД.
    """

    device = config['device']
    broker = device['broker']
    temperature = device['temp']
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


def set_gpio_status(conn, family):
    """Записать текущее состояние всех компонентов единого семейства.

    Параметры:
        :param conn: — объект соединения с БД;
        :param family: — название семейства компонентов.

    Вернуть объект соединения с БД.
    """

    timestamp = datetime.now().isoformat(sep=' ')

    for unit in family:
        tabledata = [timestamp, unit.pin, family, unit.id,
                     unit.description, str(unit.state)]
        fill_table(conn, 'gpio_status', tabledata)


def fill_table(conn, tablename, data):
    """Заполнить таблицу указанными значениями.

    Параметры:
        :param conn: — объект соединения с БД;
        :param tablename: — название целевой таблицы;
        :param data: — упорядоченная коллекция данных для заполнения.

    Вернуть объект соединения с БД.
    """
    cursor = conn.cursor()
    cursor.execute(_SQL[tablename], data)
    cursor.close()

    return conn


_SQL = {
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

    'gpio_status': '''REPLACE INTO gpio_status
                              (timestamp, pin, family, internal_name,verbose_name, state)
                       VALUES (?, ?, ?, ?, ?, ?);''',

    'gpio_status_archive': '''INSERT INTO gpio_status_archive
                                     (timestamp, pin, family, internal_name,verbose_name, state)
                              VALUES (?, ?, ?, ?, ?, ?);''',
}
