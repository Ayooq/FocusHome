import sqlite3
import uuid
from datetime import datetime
from typing import Tuple


def get_db(filename: str) -> sqlite3.Connection:
    """Возвратить объект соединения с базой данных.

    Параметры:
      :param filename: — наименование файла, в котором хранится БД.
    """

    conn = sqlite3.connect(filename, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    return conn


def init_db(filename: str, *components: dict) -> sqlite3.Connection:
    """Инициализировать локальную базу данных.

    Создать схему с таблицами:
    1) events — все зарегистрированные события;
    2) status — текущее состояние компонентов устройства;
    3) status_archive — история состояний компонентов за всё время.

    После успешного создания схемы таблицы status* заполняются
    предустановленными значениями.

    Параметры:
      :param filename: — название файла, в котором будет инициализирована БД;
      :param components: — кортеж из компонентов устройства, разбитых на группы.

    Возвратить объект соединения с БД.
    """

    conn = get_db(filename)
    cursor = conn.cursor()

    try:
        print('Инициализация базы данных...')
        _create_schema(cursor)
    except sqlite3.Error:
        conn.rollback()
        raise
    else:
        print('Таблицы созданы.')
        conn.commit()

    try:
        set_initial_status(conn, *components)
    except:
        print('Ошибка в заполнении таблиц данными по умолчанию!')
        raise
    else:
        print('Инициализация прошла успешно!')

    return conn


def _create_schema(cursor: sqlite3.Cursor) -> None:
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
        cursor: sqlite3.Cursor, tablename: str, columns: Tuple[str]) -> None:
    sql_command = '''
        CREATE TABLE {}
            (id INTEGER PRIMARY KEY,
            timestamp TEXT{}
            unit TEXT{}
            {});
        '''.format(tablename, *columns)
    cursor.execute(sql_command)


def set_initial_status(
        conn: sqlite3.Connection, *components: dict) -> sqlite3.Connection:
    """Записать первоначальное состояние всех компонентов единого семейства.

    Параметры:
      :param conn: — объект соединения с БД;
      :param components: — кортеж из компонентов устройства, разбитых на группы.

    Вернуть объект соединения с БД.
    """

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
            cursor.execute(SQL[tablename], tabledata)
        except sqlite3.Error:
            print(f'Не удалось заполнить таблицу {tablename}!')
            conn.rollback()
        else:
            print(f'Таблица {tablename} успешно заполнена.')
            conn.commit()


STATUS_TABLES_STRUCTURE = {
    'columns': '(timestamp, unit, state)',
    'values': 'VALUES (?, ?, ?);',
}

SQL = {
    'events': '''
        INSERT INTO events
            (timestamp, type, unit, message)
        VALUES (?, ?, ?, ?);
        ''',

    'status': '''
        REPLACE INTO status {} {}
        '''.format(
        STATUS_TABLES_STRUCTURE['columns'],
        STATUS_TABLES_STRUCTURE['values']
    ),

    'status_archive': '''
        INSERT INTO status_archive {} {}
        '''.format(
        STATUS_TABLES_STRUCTURE['columns'],
        STATUS_TABLES_STRUCTURE['values']
    ),
}
