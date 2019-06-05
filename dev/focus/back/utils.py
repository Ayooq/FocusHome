import os
import glob
import sqlite3
from sqlite3 import Error
from threading import Thread


root_dir = os.path.abspath(os.path.curdir)
config_file_path = '%s/config.yaml' % root_dir
log_file_path = '%s/focus.log' % root_dir


class Worker:
    """Базовый организатор обработки данных через отдельный поток."""

    def __init__(self, worker):
        self.receiver_thread = Thread(target=worker, daemon=True)
        self.receiver_thread.start()

        self.message_received = 'Обработчик не установлен!'

    def set_message_callback(self, callback):
        self.message_received = callback

    def quit(self):
        self.receiver_thread.join()


##### Работа с локальной базой данных. #####

def init_db(filename):
    try:
        conn = sqlite3.connect(filename)
        print(sqlite3.version)

        cursor = conn.cursor()
        _create_schema(cursor)
    except Error as e:
        print('Ошибка в настройке БД!', e, sep='\n\n')
    else:
        return conn


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


def set_config(conn, config):
    data = (
        config['device']['id'],
        config['device']['broker']['host'],
        config['device']['broker']['port'],
        config['device']['broker']['keepalive'],
        config['device']['temperature']['cpu']['min'],
        config['device']['temperature']['cpu']['max'],
        config['device']['temperature']['cpu']['threshold'],
        config['device']['temperature']['cpu']['hysteresis'],
        config['device']['temperature']['cpu']['timedelta'],
        config['device']['temperature']['board']['min'],
        config['device']['temperature']['board']['max'],
        config['device']['temperature']['board']['threshold'],
        config['device']['temperature']['board']['hysteresis'],
        config['device']['temperature']['board']['timedelta'],
    )

    return fill_table(conn, 'config', data)


def fill_table(conn, tablename, data):
    cursor = conn.cursor()
    cursor.execute(_SQL[tablename], data)

    return conn


##### 1-Wire #####

def get_sensor_file():
    return glob.glob('/sys/bus/w1/devices/28*/hwmon/hwmon0/temp1_input')


##### Журналирование и отправка отчётов. #####

def _log(instance, msg):
    """Зарегистрировать события согласно указанным уровням логирования."""

    instance.logger.debug(
        '%s: %s | [%s]', instance.description, msg, repr(instance))
    instance.logger.info('%s: %s', instance.description, msg)


def _report(instance, msg_type, msg_body):
    """Опубликовать сообщение о событии."""

    if msg_type:
        instance.reporter.set_type(msg_type, msg_body).report()
    else:
        instance.reporter.event(instance.description, msg_body).report()


def log_and_report(instance, msg_body, msg_type=None):
    """Опубликовать сообщение о событии и создать соответствующие записи в логе."""

    _log(instance, msg_body)
    _report(instance, msg_type, msg_body)


def register(instance, subscriber, callback):
    instance.reporter.register(subscriber, callback)


def unregister(instance, subscriber, callback):
    instance.reporter.unregister(subscriber)
