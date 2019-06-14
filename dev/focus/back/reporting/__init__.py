"""Модуль отправки сообщений посреднику, структурированных в соответствии с протоколом обмена данными MQTT.

Разрешенные типы msg_body:
_______________________________
|___[Python]___|____[JSON]____|
|dict__________|________object|
|list,_tuple___|_________array|
|str___________|________string|
|int,_float____|________number|
|True__________|__________true|
|False_________|_________false|
|None__________|__________null|

Проверять msg_body по isinstance.
"""

import json

from .Message import Message
from .Address import Address


class Reporter(Message):
    """Модель отчёта от имени экземпляра устройства либо его компонента."""

    def __init__(self, ident, mode='report'):
        self._publisher = str(ident)
        self._callbacks = {}

        super().__init__(mode)

    def register(self, subscriber, callback):
        """Зарегистрировать подписчика с указанной функцией оповещения в словаре рассылки.

        Параметры:
            :param subscriber: — уникальное имя подписчика;
            :param callback: — функция оповещения подписчика.
        """

        self._callbacks[subscriber] = callback

    def unregister(self, subscriber):
        """Удалить подписчика из словаря рассылки.

        Параметры:
            :param subscriber: — уникальное имя подписчика.
        """

        del self._callbacks[subscriber]

    def report(self):
        """Разослать отчёт всем подписчикам."""

        for subscriber in self._callbacks:
            self._send(self, subscriber)

    def _send(self, report, subscriber):
        """Отправить отчёт подписчику.

        Параметры:
            :param report: — подготовленый отчёт;
            :param subscriber: — уникальное имя подписчика.

        Возвратить функцию-обработчик для подписчика либо
        осуществить тестовый вывод отчёта на экран при ошибке.
        """

        addr = Address(self._publisher, subscriber)
        report.update(addr)

        try:
            func = self._callbacks[subscriber]
            return func(report)
        except Exception:
            self._dumper(report)
            pass

    def _dumper(self, doc):
        """Тестовый вывод."""

        print('Печатаю', json.dumps(doc))
