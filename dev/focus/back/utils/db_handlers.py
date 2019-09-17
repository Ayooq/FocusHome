"""Модуль взаимодействия с локальной базой данных.

Функции:
    :func get_db(filename): — вернуть объект соединения с базой данных;
    :func init_db(device, filename, *components): — инициализировать локальную
базу данных;
    :func fill_table(conn, cursor, tables_set, tabledata): — заполнить таблицы
указанными значениями.
"""
import sqlite3
import uuid
from datetime import datetime
from typing import Tuple, Type

from .messaging_tools import notify

Conn = sqlite3.Connection
Cursor = sqlite3.Cursor


def get_db(filename: str) -> Conn:
    """Вернуть объект соединения с базой данных.

    Параметры:
        :param filename: — наименование файла, в котором хранится БД.
    """
    conn = sqlite3.connect(filename, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    return conn


def init_db(device: Type[dict], filename: str, *components: Type[dict]) -> Conn:
    """Инициализировать локальную базу данных.

    Создать схему с таблицами:
    1) events — все зарегистрированные события;
    2) status — текущее состояние компонентов устройства;
    3) status_archive — история состояний компонентов за всё время.

    После успешного создания схемы таблицы status* заполняются
    предустановленными значениями.

    Параметры:
        :param device: — экземпляр объекта устройства;
        :param filename: — название файла, в котором будет инициализирована БД;
        :param components: — кортеж из компонентов устройства.

    Вернуть объект соединения с БД.
    """
    conn = get_db(filename)
    cursor = conn.cursor()

    try:
        msg_body = 'Инициализация базы данных...'
        notify(device, msg_body, swap=True, type_='info')
        _create_schema(cursor)
    except sqlite3.Error:
        conn.rollback()
        raise
    else:
        notify(device, 'Таблицы созданы.', swap=True, type_='info')
        conn.commit()

    try:
        _set_initial_status(conn, *components)
    except:
        msg_body = 'Ошибка в заполнении таблиц данными по умолчанию!'
        notify(device, msg_body, swap=True, type_='error')

        raise
    else:
        msg_body = 'Инициализация прошла успешно!'
        notify(device, msg_body, swap=True, type_='info')

    return conn


def _create_schema(cursor: Cursor) -> None:
    mapping = {
        'events': (
            ', type TEXT,',
            ',',
            'message TEXT',
        ),
        'status': (
            ',',
            ' UNIQUE,',
            'state TEXT',
        ),
        'status_archive': (
            ',',
            ',',
            'state TEXT',
        ),
    }

    for table, columns in mapping.items():
        _create_bootstrapped_table(cursor, table, columns)


def _create_bootstrapped_table(
        cursor: Cursor, tablename: str, columns: Tuple[str]) -> None:
    sql_command = '''
        CREATE TABLE {}
            (id INTEGER PRIMARY KEY,
            timestamp TEXT{}
            unit TEXT{}
            {});
        '''.format(tablename, *columns)
    cursor.execute(sql_command)


def _set_initial_status(conn: Conn, *components: dict) -> Conn:
    timestamp = datetime.now().isoformat(sep=' ')
    tables_set = {'status', 'status_archive'}
    cursor = conn.cursor()

    for component in components:
        for family, group in component.items():
            for k, v in group.items():
                if family == 'couts':
                    for _ in (v.control, v.socket):
                        tabledata = [timestamp, _.id, _.state]
                        fill_table(conn, cursor, tables_set, tabledata)
                else:
                    tabledata = [timestamp, k, v.state]
                    fill_table(conn, cursor, tables_set, tabledata)

    return conn


def fill_table(
    conn: sqlite3.Connection,
    cursor: sqlite3.Cursor,
    tables_set: set,
    tabledata: list
) -> None:
    """Заполнить таблицы указанными значениями.

    Параметры:
        :param conn: — объект соединения с БД;
        :param cursor: — объект указателя БД;
        :param tables_set: — набор наименований целевых таблиц;
        :param tabledata: — список данных для заполнения таблицы.
    """
    for tablename in tables_set:
        try:
            cursor.execute(_SQL[tablename], tabledata)
        except sqlite3.Error:
            print(f'Не удалось заполнить таблицу {tablename}!')
            conn.rollback()
        else:
            print(f'Таблица {tablename} успешно заполнена.')
            conn.commit()


_STATUS_TABLES_STRUCTURE = {
    'columns': '(timestamp, unit, state)',
    'values': 'VALUES (?, ?, ?);',
}

_SQL = {
    'events': '''
        INSERT INTO events
            (timestamp, type, unit, message)
        VALUES (?, ?, ?, ?);
        ''',

    'status': '''
        REPLACE INTO status {} {}
        '''.format(
        _STATUS_TABLES_STRUCTURE['columns'],
        _STATUS_TABLES_STRUCTURE['values']
    ),

    'status_archive': '''
        INSERT INTO status_archive {} {}
        '''.format(
        _STATUS_TABLES_STRUCTURE['columns'],
        _STATUS_TABLES_STRUCTURE['values']
    ),
}
