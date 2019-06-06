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

from .Report import Report
from .Address import Address


class Reporter(Report):
    """Модель отчёта от имени указанного устройства либо его компонента."""

    def __init__(self, ident):
        self._publisher = str(ident)
        self._callbacks = {}
        super().__init__()

    def register(self, subscriber, callback):
        """Зарегистрировать подписчика с указанной функцией оповещения в словаре рассылки.

        Параметры:
        \t:param subscriber: уникальное имя подписчика.
        \t:param callback: функция оповещения подписчика.
        """

        self._callbacks[subscriber] = callback

    def unregister(self, subscriber):
        """Удалить подписчика из словаря рассылки.

        Параметры:
        \t:param subscriber: уникальное имя подписчика.
        """

        del self._callbacks[subscriber]

    def report(self):
        """Разослать отчёт всем подписчикам."""

        for subscriber in self._callbacks:
            self._send(self, subscriber)

    def _send(self, report, subscriber):
        """Отправить подготовленный отчёт подписчику.

        Параметры:
        \t:param report: подготовленый отчёт.
        \t:param subscriber: уникальное имя подписчика.
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
