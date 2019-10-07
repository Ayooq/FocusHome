"""Инструменты для взаимодействия с локальной базой данных.

:function get_db(filename): вернуть объект соединения с БД
:function init_db(device, filename, *components): инициализировать локальную БД
:function fill_table(conn, cursor, tables_set, tabledata): заполнить таблицу БД
"""
import sqlite3
import uuid
from datetime import datetime
from typing import Tuple, Type

from ..hardware import Hardware
from .messaging import notify

Conn = sqlite3.Connection
Cursor = sqlite3.Cursor


def get_db(filename: str) -> Conn:
    """Вернуть объект соединения с базой данных.

    :param filename: наименование файла, в котором хранится БД
    :type filename: str

    :return: объект БД
    :rtype: sqlite3.Connection
    """
    conn = sqlite3.connect(filename, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    return conn


def init_db(device: Type[Hardware], filename: str, hardware: dict) -> Conn:
    """Инициализировать локальную базу данных.

    Создать схему с таблицами:
    1) events — все зарегистрированные события;
    2) status — текущее состояние компонентов устройства;
    3) status_archive — история состояний компонентов за всё время.

    После успешного создания схемы таблицы status* заполняются
    предустановленными значениями.

    :param device: экземпляр объекта устройства
    :type device: Type[Hardware]
    :param filename: наименование файла, в котором инициализирована БД
    :type filename: str
    :param hardware: компоненты устройства
    :type hardware: dict

    :return: объект БД
    :rtype: sqlite3.Connection
    """
    conn = get_db(filename)
    cursor = conn.cursor()

    try:
        msg = 'инициализация базы данных...'
        notify(device, msg, no_repr=True, local_only=True)
        _create_schema(cursor)
    except sqlite3.Error:
        conn.rollback()
        raise
    else:
        notify(device, 'таблицы созданы.', no_repr=True, local_only=True)
        conn.commit()

    try:
        _set_initial_status(conn, hardware)
    except:
        msg = 'ошибка в заполнении таблиц данными по умолчанию!'
        notify(device, msg, no_repr=True, local_only=True)

        raise
    else:
        msg = 'инициализация прошла успешно!'
        notify(device, msg, no_repr=True, local_only=True)

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


def _set_initial_status(conn: Conn, hardware: dict) -> Conn:
    timestamp = datetime.now().isoformat(sep=' ')
    tables_set = {'status', 'status_archive'}
    cursor = conn.cursor()

    for group_families in hardware.values():
        for family_components in group_families.values():
            for uid, component in family_components.items():
                tabledata = [timestamp, uid, component.state]
                fill_table(conn, cursor, tables_set, tabledata)

    return conn


def fill_table(
        conn: Conn, cursor: Cursor, tables_set: set, tabledata: list) -> None:
    """Заполнить таблицы указанными значениями.

    :param conn: объект соединения с БД
    :type conn: sqlite3.Connection
    :param cursor: объект указателя БД
    :type cursor: sqlite3.Cursor
    :param tables_set: набор наименований целевых таблиц
    :type tables_set: set
    :param tabledata: данные для заполнения таблицы
    :type tabledata: list
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
