import sqlite3
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
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS messages
                        (device_id INTEGER NOT NULL PRIMARY KEY,
                        pin INTEGER NOT NULL UNIQUE,
                        component NOT NULL TEXT UNIQUE,
                        msg_body TEXT);
                CREATE TABLE IF NOT EXISTS current_out_status
                        (device_id INTEGER NOT NULL PRIMARY KEY,
                        pin INTEGER NOT NULL UNIQUE,
                        msg_body TEXT);
                CREATE TABLE IF NOT EXISTS status_archive
                        (device_id INTEGER NOT NULL PRIMARY KEY,
                        pin INTEGER NOT NULL UNIQUE,
                        msg_body TEXT);
                CREATE TABLE IF NOT EXISTS config
                        (device_id INTEGER NOT NULL PRIMARY KEY,
                        device_name TEXT NOT NULL UNIQUE,
                        keepalive INTEGER NOT NULL CHECK(keepalive > 3),
                        cpu_min REAL CHECK(cpu_min > 0),
                        cpu_max REAL CHECK(cpu_max < 200),
                        cpu_threshold REAL,
                        cpu_delta REAL,
                        board_min REAL CHECK(board_min > 0),
                        board_max REAL CHECK(board_max < 200),
                        board_threshold REAL,
                        board_delta REAL);'''
    )
