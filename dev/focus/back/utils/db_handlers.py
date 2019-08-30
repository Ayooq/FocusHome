import sqlite3
import uuid
from datetime import datetime


def init_db(filename: str, config: dict, units: dict):
    """Инициализировать БД SQLite3 в файле с именем :param filename:.

    Создать схему с таблицами:
    1) events — все зарегистрированные события;
    2) status — текущее состояние компонентов устройства;
    3) status_archive — история состояний компонентов за всё время;
    4) routines — доступные рутины.

    Схема создаётся единожды при самом первом запуске устройства.
    Это обеспечивается проверкой наличия непустых строк в указанном файле.

    После успешного создания схемы таблицы status* заполняются
    предустановленными значениями.

    Возвратить объект соединения с БД.
    """

    conn = sqlite3.connect(filename, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    db_file = open(filename, 'rb')
    db_initiated = db_file.read(1)
    db_file.close()

    if not db_initiated:
        cursor = conn.cursor()

        try:
            print('Инициализация БД...')
            _create_schema(cursor)
        except sqlite3.Error:
            conn.rollback()
            raise
        else:
            print('Таблицы созданы.')
            conn.commit()

        try:
            set_initial_status(conn, units)
        except:
            print('Ошибка в заполнении таблиц данными по умолчанию!')
            raise
        else:
            print('Инициализация БД прошла успешно!')
    else:
        print('Локальная БД уже существует. Инициализация не требуется.')

    return conn


def _create_schema(cursor):
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


def _create_bootstrapped_table(cursor, name, columns):
    sql_command = '''
        CREATE TABLE {}
            (id INTEGER PRIMARY KEY,
            timestamp TEXT{}
            unit TEXT{}
            {});
        '''.format(name, *columns)
    cursor.execute(sql_command)


def set_initial_status(conn, units: dict):
    """Записать первоначальное состояние всех компонентов единого семейства.

    Параметры:
      :param conn: — объект соединения с БД;
      :param units: — кортеж из семейств компонентов устройства.

    Вернуть объект соединения с БД.
    """

    timestamp = datetime.now().isoformat(sep=' ')
    cursor = conn.cursor()
    tables_set = {'status', 'status_archive'}

    for family, group in units.items():
        for k, v in group.items():
            if family == 'couts':
                for _ in (v.control, v.socket):
                    tabledata = [timestamp, _.id, _.state]
                    fill_table(conn, cursor, tables_set, tabledata)
            else:
                tabledata = [timestamp, k, v.state]
                fill_table(conn, cursor, tables_set, tabledata)

    return conn


def fill_table(conn, cursor, tables_set: set, tabledata):
    """Заполнить таблицы указанными значениями.

    Параметры:
      :param conn: — объект соединения с БД;
      :param cursor: — объект указателя БД;
      :param tables_set: — набор наименований целевых таблиц;
      :param tabledata: — упорядоченная коллекция данных для заполнения.
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
