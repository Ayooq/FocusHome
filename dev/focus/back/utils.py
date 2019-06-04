import glob
import sqlite3
from sqlite3 import Error
from threading import Thread


class Worker:
    """Базовый организатор обмена через отдельный поток."""

    def __init__(self, worker):
        self.receiver_thread = Thread(target=worker, daemon=True)
        self.receiver_thread.start()

        self.message_received = 'Обработчик не установлен!'

    def set_message_callback(self, callback):
        self.message_received = callback

    def quit(self):
        self.receiver_thread.join()


def init_db(filename):
    try:
        conn = sqlite3.connect(filename)
        print(sqlite3.version)

        cursor = conn.cursor()
        create_scheme(cursor)
    except Error as e:
        print(e)
    else:
        return conn


def create_scheme(cursor):
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS config
                  (id INTEGER PRIMARY KEY,
                  device TEXT NOT NULL UNIQUE,
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
                  device TEXT,
                  pin INTEGER,
                  group TEXT,
                  internal_name TEXT,
                  verbose_name TEXT,
                  state TEXT);

           CREATE TABLE IF NOT EXISTS gpio_status_archive
                  (id INTEGER PRIMARY KEY,
                  device TEXT,
                  pin INTEGER,
                  group TEXT,
                  internal_name TEXT,
                  verbose_name TEXT,
                  state TEXT);'''
    )


def set_config(conn, config):
    sql = '''INSERT INTO config
                    (device, keepalive, cpu_min, cpu_max,
                    cpu_threshold, cpu_hysteresis, cpu_timedelta,
                    board_min, board_max, board_threshold,
                    board_hysteresis, board_timedelta)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

    cursor = conn.cursor()
    cursor.execute(sql, config)

    return conn


def get_sensor_file():
    return glob.glob('/sys/bus/w1/devices/28*/hwmon/hwmon0/temp1_input')
