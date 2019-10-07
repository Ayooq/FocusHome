import json
from typing import Any, Callable, NoReturn, Type, Union

from ..utils.messaging import _log


class Reporter(dict):
    """Модель отчёта от имени экземпляра устройства либо его компонента.

    Методы:
        :meth __init__(self, id_): — инициализировать экземпляр класса;
        :meth register(self, subscriber, callback): — зарегистрировать в словаре
    рассылки сообщений подписчика с указанной функцией оповещения;
        :meth unregister(self, subscriber): — удалить подписчика из словаря
    рассылки сообщений;
        :meth inscribe(self, values): — заполнить отчёт данными;
        :meth report(self): — разослать отчёт подписчикам.
    """

    def __init__(self, id_: str) -> None:
        super().__init__()

        self.id = id_
        self.mapping = 'from', 'type', 'message', 'qos', 'retain'
        self._callbacks = {}

    def register(
            self, subscriber: str, callback: Callable, *args) -> None:
        """Зарегистрировать в словаре рассылки сообщений подписчика с указанными
        функциями оповещения.

        Параметры:
            :param subscriber: — уникальное имя подписчика;
            :param callbacks: — произвольное количество функций оповещения.
        """
        self._callbacks[subscriber] = callback, *args

    def unregister(self, subscriber: str) -> None:
        """Удалить подписчика из словаря рассылки сообщений.

        Параметры:
            :param subscriber: — уникальное имя подписчика.
        """
        del self._callbacks[subscriber]

    def fill_in(self, values: tuple) -> None:
        """Заполнить отчёт данными.

        Параметры:
            :param values: — кортеж данных для заполнения отчёта.
        """
        data = zip(self.mapping, values)
        self.update(data)

    def report(self) -> None:
        """Разослать отчёт подписчикам."""
        for subscriber in self._callbacks:
            self._send(report=self, subscriber=subscriber)

    def _send(
        self,
        report: Type[dict],
        subscriber: str
    ) -> Union[Any, NoReturn]:
        callback, *args = self._callbacks[subscriber]

        try:
            return callback(report, *args)
        except:
            print(self)

            raise

    # def _dump(self, report: Type[dict]) -> None:
    #     res = json.dumps(report)

    #     print('Печатаю:', end='')

    #     for i in res.split('{'):
    #         print(i)
