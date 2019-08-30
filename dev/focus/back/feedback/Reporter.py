import json

from .Message import Message


class Reporter(Message):
    """Модель отчёта от имени экземпляра устройства либо его компонента."""

    def __init__(self, id_, topic='report'):
        self.id = id_
        self._callbacks = {}

        super().__init__(topic)

    def register(self, subscriber: str, callback):
        """Зарегистрировать подписчика с указанной функцией оповещения в словаре рассылки.

        Параметры:
          :param subscriber: — уникальное имя подписчика;
          :param callback: — функция оповещения подписчика.
        """

        self._callbacks[subscriber] = callback

    def unregister(self, subscriber: str):
        """Удалить подписчика из словаря рассылки.

        Параметры:
          :param subscriber: — уникальное имя подписчика.
        """

        del self._callbacks[subscriber]

    def report(self):
        """Разослать отчёт всем подписчикам."""

        for subscriber in self._callbacks:
            self._send(self, subscriber)

    def _send(self, report: dict, subscriber: str):
        """Отправить отчёт подписчику.

        Параметры:
          :param report: — подготовленый отчёт;
          :param subscriber: — уникальное имя подписчика.

        Возвратить функцию-обработчик для подписчика либо
        осуществить тестовый вывод отчёта на экран при ошибке.
        """

        try:
            func = self._callbacks[subscriber]
            return func(report)
        except Exception:
            self._dump(report)
            raise

    def _dump(self, report: dict):
        """Тестовый вывод.

        Параметры:
          :param report: — объект отчёта.
        """

        dump = json.dumps(report)

        print('Печатаю:', end='')

        for i in dump.split('{'):
            print(i)
