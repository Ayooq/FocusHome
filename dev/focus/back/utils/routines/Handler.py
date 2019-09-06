import shelve
import sqlite3
from typing import Any, Callable, List, Tuple

from .. import ROUTINES_FILE
from ..messaging_tools import notify


class Handler:
    """Обработчик рутин."""

    def dispatch_routines(
            self, routines: List[Tuple[int, Callable, list]]) -> None:
        """Передать полученные рутины соответствующим обработчикам.

        Если обработчик для рутины не определён, занести в реестр новые данные.

        Параметры:
          :param routines: — список рутин в виде кортежей: (
              <идентификатор>,
              <обработчик>,
              <аргументы>,
          )
        """

        with shelve.open(ROUTINES_FILE, flag='r', protocol=4) as db:
            new_routines = []
            known_routines = []

            for routine in routines:
                if routine[0] in db.keys():
                    known_routines.append(routine)
                else:
                    new_routines.append(routine)

        if new_routines:
            self.register_routines(new_routines)

        res = new_routines + known_routines

        for r in res:
            self.execute_routine(r)

    def execute_routine(
            self,
            routine: Tuple[int, Callable, list],
            db: shelve.Shelf
    ) -> Any:
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

        Вернуть результат выполнения рутины.
        """

        key, _, args = routine

        return db[key](args)

    def register_routines(
            self, routines: List[Tuple[int, Callable, list]]) -> None:
        """Зарегистрировать полученные рутины в специализированную БД.

        БД реализует интерфейс словаря, в который записываются данные вида
        <ключ: значение>. Каждому новому ключу присваивается свой обработчик
        для конкретной рутины. Аргументы на данном этапе не передаются.

        Параметры:
          :param routines: — список рутин в виде кортежей из трёх элементов
        (числовой идентификатор для использования в качестве ключа,
        объект функции-обработчика рутины, выступающий в роли значения по ключу,
        и список аргументов для исполнения конкретной рутины).
        """

        with shelve.open(ROUTINES_FILE, protocol=4) as db:
            for i in routines:
                key, handler, _ = i
                db[key] = handler
