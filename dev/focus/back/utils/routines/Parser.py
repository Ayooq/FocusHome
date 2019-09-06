import os
import sqlite3
from typing import List

# from .Handler import Handler
from ..concurrency import CoroWorker


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
        self,
        conn: sqlite3.Connection,
        payload: dict
    ) -> List[dict]:
        """Разбить инструкции на составляющие для последующей обработки."""

        for k, v in payload['instruction'].items():
            coros = []

            if k == 'routine':
                routine = {}
                actions = v.get('actions')
                conditions = v.get('conditions')

                if conditions:
                    cursor = conn.cursor()
                    routine['conditions'] = self.parse_conditions(
                        cursor, conditions)

                if actions:
                    routine['actions'] = self.parse_actions(actions)

                coros.append(routine)

            return coros

    def parse_conditions(self, cursor: sqlite3.Cursor, conditions: list) -> str:
        """Рекурсивно распарсить условия выполнения рутины.

        Обрабатывает три типа данных: словарь (1), строку (2) и список (3).
        1) содержит данные для сравнения на истинность, которые
        обрабатываются вложенной функцией;
        2) добавляется в результирующий список для вычислений как оператор;
        3) вызывает эту же функцию рекурсивно с собой в качестве аргумента.

        Параметры:
        :param cursor: — указатель для работы с БД;
        :param conditions: — список условий для проверки на истинность.

        Вернуть строку для вычисления итогового выражения.
        """

        expr = []

        for c in conditions:
            if isinstance(c, dict):
                c = self.check_conditions(cursor, c)
            elif isinstance(c, list):
                c = self.parse_conditions(cursor, c)
            expr.append(str(c))

        return ' '.join(expr)

    def check_conditions(
            self, cursor: sqlite3.Cursor, conditions: dict) -> bool:
        """Проверить условия, составленные из элементов словаря, на истинность.

        Параметры:
        :param cursor: — указатель для работы с БД;
        :param conditions: — словарь проверяемых условий.

        Вернуть результат вычисления итоговой строки, составленной из значений
        элементов словаря.
        """

        cursor.execute('''
            SELECT state
            FROM status
            WHERE unit = ?;
            ''', (conditions['unit'], )
        )

        state = cursor.fetchone()[0]
        operator = conditions['compare']

        try:
            operator = Parser.operators[operator]
        except KeyError:
            print('Оператора с таких названием нет среди допустимых ключей.')

            raise

        value = conditions['value']

        return eval(f'{state} {operator} {value}')

    def parse_actions(self, actions: List[dict]) -> List[dict]:
        """Распарсить список действий для переданной рутины.

        Параметры:
          :param actions: — список, в котором указаны заданные действия в форме
        словарей.

        Вернуть список словарей распарсенных действий.
        """

        parsed_actions = []

        for a in actions:
            action_type = a['action']
            action = {}

            if action_type == 'call':
                action['callback'] = a['function']
                action['arguments'] = a['params']

            elif action_type == 'setValue':
                action['component'] = a['unit']
                action['value'] = a['value']

            parsed_actions.append(action)

        return parsed_actions
