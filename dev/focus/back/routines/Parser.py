import os
import sqlite3
from typing import Dict, List, Tuple


class Parser:
    """Парсер поступающих команд."""

    operators = {
        'eq': '==',
        'ne': '!=',
        'lt': '<',
        'gt': '>',
        'le': '<=',
        'ge': '>=',
    }

    def parse_instructions(
            self, conn: sqlite3.Connection, payload: dict) -> Dict[list]:
        """Разбить инструкции на составляющие для последующей обработки.

        Параметры:
          :param conn: — объект локальной базы данных;
          :param payload: — словарь с инструкциями, который нужно распарсить.

        Вернуть словарь, содержащий распарсенные рутины/команды.
        """
        id_ = payload.get('routine_id')
        res = {'routines': [], 'commands': []}

        for k, v in payload['instruction'].items():
            if k == 'routine':
                conditions = v.get('conditions')
                actions = v.get('actions')
                actions = self.parse_actions(actions)
                command = [id_, actions]

                if conditions:
                    cursor = conn.cursor()
                    conditions = self.parse_conditions(cursor, conditions)
                    command.append(conditions)
                    res['routines'].append(command)
                else:
                    res['commands'].append(command)

        return res

    def parse_conditions(self, cursor: sqlite3.Cursor, conditions: list) -> str:
        """Рекурсивно распарсить условия выполнения рутины.

        Обрабатывает три типа данных: словарь (1), строку (2) и список (3).
        1) содержит данные для сравнения на истинность, которые обрабатываются
        вложенной функцией;
        2) добавляется в результирующий список для вычислений как оператор;
        3) вызывает эту же функцию рекурсивно с собой в качестве 2-го аргумента.

        Параметры:
        :param cursor: — указатель для работы с БД;
        :param conditions: — список условий для проверки на истинность.

        Вернуть список условий для дальнейшей обработки.
        """
        res = []

        for c in conditions:
            if isinstance(c, list):
                # Вернуть список:
                c = self.parse_conditions(cursor, c)
            elif isinstance(c, dict):
                # Вернуть кортеж:
                c = self.compose_expression(cursor, c)

            res.append(c)

        # [[(sql, op, val), 'and', (sql, op, val)], 'or' (sql, op, val)]
        return res

    def compose_expression(
        self,
        cursor: sqlite3.Cursor,
        condition: dict
    ) -> Tuple[Tuple[str, Tuple[str]], str, str]:
        """Составить выражение для проверки условия из элементов словаря.

        Параметры:
        :param cursor: — указатель для работы с БД;
        :param condition: — словарь проверяемогшо условия.

        Вернуть кортеж, состоящий из вложенного кортежа сформированного
        SQL-запроса и двух строк — оператора сравнения и сравниваемого значения.
        """
        SQL = ('''
            SELECT state
            FROM status
            WHERE unit = ?;
            ''', (condition['unit'], )
               )
        operator = condition['compare']
        value = condition['value']

        try:
            operator = Parser.operators[operator]
        except KeyError:
            print('Оператора с таким названием нет среди допустимых ключей.')

            raise

        return SQL, operator, value

        # cursor.execute('''
        #     SELECT state
        #     FROM status
        #     WHERE unit = ?;
        #     ''', (conditions['unit'], )
        # )

        # state = cursor.fetchone()[0]

        # return eval(f'{state} {operator} {value}')

    def parse_actions(self, actions: List[dict]) -> List[str, str, dict]:
        """Распарсить список действий для переданной рутины.

        Параметры:
          :param actions: — список, в котором указаны заданные действия в форме
        словарей.

        Вернуть список словарей распарсенных действий.
        """

        parsed_actions = []

        for a in actions:
            component = a['unit'],
            callback = a['function']
            kwargs = {}

            for i in a['params']:
                kwargs.update({i['name']: i['value']})

            parsed_actions.append((component, callback, kwargs))

        return parsed_actions
