import asyncio
import os
import shelve
import sqlite3

from .. import DB_FILE
from ..concurrency.Worker import Worker
from ..messaging_tools import log_and_report

operators = {
    'eq': '==',
    'ne': '!=',
    'lt': '<',
    'gt': '>',
    'le': '<=',
    'ge': '>=',
}

payload = {
    "instruction": {
        "routine": {
            "conditions": [
                [
                    {"unit": "in1", "compare": "eq", "value": "0"},
                    "and",
                    {"unit": "in2", "compare": "eq", "value": "1"}
                ],
                "or",
                {"unit": "cpu", "compare": "gt", "value": "80"}
            ],
            "actions": [
                {
                    "action": "call",
                    "unit": "",
                    "value": "",
                    "function": "run_fan",
                    "params": [
                        {"name": "speed", "value": "500"},
                        {"name": "min_temp", "value": "60"}
                    ]
                }
            ]
        }
    }
}


def parse_actions(actions):
    """Распарсить список действий для переданной рутины."""

    for a in actions:
        action_type = a['action']

        if action_type == 'call':
            fn = a['function']
            args = a['params']
        elif action_type == 'setValue':
            unit = a['unit']
            val = a['value']

        try:
            Handler.dispatch_routines(fn, args)
        except KeyError:
            Handler.register_routines(unit, val)


def parse_instructions(conn, payload):
    """Разбить инструкции на составляющие для последующей обработки."""

    for k, v in payload['instruction'].items():
        if k == 'routine':
            routine = {'eval': [], 'then': None}
            actions = v.get('actions')
            conditions = v.get('conditions')

            if conditions:
                cursor = conn.cursor()
                routine['eval'] = parse_conditions(cursor, conditions)

            if actions:
                routine['then'] = parse_actions(actions)

            Handler.dispatch_routine(routine)


def parse_conditions(cursor, conditions):
    """Рекурсивно распарсить условия выполнения рутины.

    Обрабатывает три типа данных: словарь (1), строку (2) и список (3).
    1) содержит данные для сравнения на истинность, которые
    обрабатываются вложенной функцией;
    2) добавляется в результирующий список для вычислений как оператор;
    3) вызывает эту же функцию рекурсивно с собой в качестве аргумента.

    Параметры:
      :param cursor: — указатель для работы с БД;
      :param conditions: — список условий для проверки на истинность.

    Вернуть результат вычисления итогового выражения.
    """

    expr = []

    for c in conditions:
        if isinstance(c, dict):
            c = check_condition(cursor, c)
        elif isinstance(c, list):
            c = parse_conditions(cursor, c)
        expr.append(str(c))

    return ' '.join(expr)


def check_condition(cursor, condition):
    """Проверить условие, составленное из элементов словаря, на истинность.

    Параметры:
      :param cursor: — указатель для работы с БД;
      :param condition: — словарь проверяемых условий.

    Вернуть результат вычисления итоговой строки, составленной из значений
    элементов словаря.
    """

    cursor.execute('''
        SELECT state
        FROM status
        WHERE unit = ?;
        ''', (condition['unit'], )
    )

    state = cursor.fetchone()[0]
    operator = operators[condition['compare']]
    value = condition['value']

    return eval(f'{state} {operator} {value}')


class Handler:
    """Обработчик рутин."""

    def __init__(self, reporter):
        self.reporter = reporter
        self.worker = Worker

    def register_routines(self, routines):
        """Зарегистрировать полученные рутины в специализированную БД.

        БД реализует интерфейс словаря, в который записываются данные вида
        <ключ: значение>. Каждому новому ключу присваивается свой обработчик
        для конкретной рутины. Аргументы на данном этапе не передаются.

        Параметры:
          :param routines: — коллекция рутин в виде кортежей из трёх элементов
        (числовой идентификатор для использования в качестве ключа,
        объект функции-обработчика рутины, выступающий в роли значения по ключу,
        и коллекция аргументов для исполнения конкретной рутины).
        """

        with shelve.open('routines', protocol=4) as db:
            for i in routines:
                key, handler, _ = i
                db[key] = handler

    def dispatch_routines(self, routines):
        """Передать полученные рутины соответствующим обработчикам.

        Если обработчик для рутины не определён, занести в реестр новые данные.

        Параметры:
          :param routines: — коллекция рутин в виде кортежей (
              <идентификатор>,
              <обработчик>,
              <аргументы>,
          )
          :param command: — строковый идентификатор команды;
          :param conditions: — условия, при которых будет исполняться команда.
        """

        with shelve.open('routines', flag='r', protocol=4) as db:
            new_routines = []

            for routine in routines:
                try:
                    self.execute_routine(routine, db)
                except KeyError:
                    new_routines.append(routine)

        if new_routines:
            self.register_routines(new_routines)
            self.dispatch_routines(new_routines)

    async def execute_routine(self, routine: tuple, db):
        """Инициализировать исполнение переданной рутины.

        Для вызова обработчика используются его числовой идентификатор, с
        помощью которого объект ищется в БД, и коллекция аргументов,
        передаваемая обработчику на исполнение. Сам объект обработчика,
        содержащийся в кортеже routine, на данном этапе не используется.

        Параметры:
          :param routine: — кортеж, содержащий числовой идентификатор
        обработчика, саму функцию-обработчик и аргументы для её выполнения;
          :param db: — файл БД для извлечения из неё соответствующего
        обработчика по ключу в виде числового идентификатора;

        Вернуть результат выполнения функции.
        """

        key, _, args = routine

        return await db[key](args)


def on_event(self, event, changed_unit, target_unit, time_limit=0):
    current_state = changed_unit.state

    while time_limit:
        if changed_unit.state != current_state:
            return

        time_limit -= 1

    os.system('sudo reboot') if event == 'reload' else target_unit.toggle()

    return target_unit.state
