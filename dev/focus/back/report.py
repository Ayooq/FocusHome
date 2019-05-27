"""Словарь сообщений для сериализации JSON.

Разрешенные типы body:
_______________________________
|   [Python]   |    [JSON]    |
|--------------|--------------|
|dict          |        object|
|list, tuple   |         array|
|str           |        string|
|int, float    |        number|
|true          |          true|
|false         |         false|
|None          |          null|

Проверять body по isinstance.
"""

import json
from datetime import datetime


class Message(dict):
    """Сообщение для отчёта, оформленное в соответствии с указанным типом."""

    def __init__(self, mode):
        super().__init__()
        self._content = mode
        self.setdefault(mode, Content())

    def _formalize(self, msg_type, head, body):
        """Официально оформить содержимое."""

        payload = self[self._content]
        payload.inscribe(msg_type, head, body)


class Content(dict):
    """Структура содержимого для сообщений."""

    _subkeys = (
        'type',
        'head',
        'body'
    )

    def __init__(self):
        super().__init__()

        for key in Content._subkeys:
            self.setdefault(key)

    def inscribe(self, msg_type, head, body):
        """Вписать содержимое."""

        self['type'] = msg_type
        self['head'] = head
        self['body'] = body


class Address(dict):
    """Адресация сообщений."""

    def __init__(self, sender, receiver):
        super().__init__()

        self['from'] = sender
        self['to'] = receiver

        now = datetime.today()
        self['date'] = now.strftime('%Y%m%d%H%M%S')

    def get(self, report):
        return (report.get('from', 'system'), report.get('to', 'anybody'))


class Report(Message):
    """Отчёт на основе сообщения по указанному типу."""

    def __init__(self, msg_type=None, head=None, body=None, mode='report'):
        super().__init__(mode)

    def event(self, head, body):
        self._formalize('event', head, body)
        return self

    def info(self, head, body):
        self._formalize('info', head, body)
        return self

    def warning(self, head, body):
        self._formalize('warning', head, body)
        return self

    def error(self, head, body):
        self._formalize('error', head, body)
        return self

    def set_type(self, msg_type, head, body):
        self._formalize(msg_type, head, body)
        return self


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
        \t:param callback: функция оповещения на подписчике.
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