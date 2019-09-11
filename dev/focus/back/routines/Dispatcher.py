import shelve
import sqlite3
from typing import Any, Callable, Dict, List, Tuple

import yaml

from ..utils import BACKUP_FILE, CONFIG_FILE, ROUTINES_FILE
from ..utils.messaging_tools import notify
from . import Aggregator


class Dispatcher:
    """Распределитель команд."""

    def dispatch(
            self, *instructions: Dict[list]) -> None:
        """Передать полученные рутины соответствующим обработчикам.

        Если обработчик для рутины не определён, занести в реестр новые данные.

        Параметры:
          :param instructions: — список рутин в виде кортежей: (
              <идентификатор>,
              <обработчик>,
              <аргументы>,
          )
        """

        for cmd in instructions.get('commands'):
            self.execute_command(cmd)
        for routine in instructions.get('routines'):

        if new_commands:
            self.register_commands(new_commands)

        res = new_commands + known_commands

        for r in res:
            self.execute_command(r)

    def execute_command(
            self,
            command: Tuple[int, Callable, list],
            db: shelve.Shelf
    ) -> Any:
        """Инициализировать исполнение переданной рутины.

        Для вызова обработчика используются его числовой идентификатор, с
        помощью которого объект ищется в БД, и коллекция аргументов,
        передаваемая обработчику на исполнение. Сам объект обработчика,
        содержащийся в кортеже command, на данном этапе не используется.

        Параметры:
          :param command: — кортеж, содержащий числовой идентификатор
        обработчика, саму функцию-обработчик и аргументы для её выполнения;
          :param db: — файл БД для извлечения из неё соответствующего
        обработчика по ключу в виде числового идентификатора;

        Вернуть результат выполнения рутины.
        """

        id_, actions = command

        for action in actions:
            component, callback, kwargs = action
            Aggregator.execute(component, callback, kwargs)

    def register_commands(
            self, commands: List[Tuple[int, Callable, list]]) -> None:
        """Зарегистрировать полученные рутины в специализированную БД.

        БД реализует интерфейс словаря, в который записываются данные вида
        <ключ: значение>. Каждому новому ключу присваивается свой обработчик
        для конкретной рутины. Аргументы на данном этапе не передаются.

        Параметры:
          :param commands: — список рутин в виде кортежей из трёх элементов
        (числовой идентификатор для использования в качестве ключа,
        объект функции-обработчика рутины, выступающий в роли значения по ключу,
        и список аргументов для исполнения конкретной рутины).
        """

        with shelve.open(ROUTINES_FILE, protocol=4) as db:
            for i in commands:
                key, handler, _ = i
                db[key] = handler
