import sqlite3
from datetime import datetime as dt
from datetime import timedelta as td
from typing import Any

from ..utils.messaging_tools import notify


class Aggregator:
    """Агрегатор рутин."""

    _callbacks = {
        'on': on,
        'off': off,
        'toggle': toggle,
        'set_state': set_state,
        'reboot': reboot,
    }

    def execute(self, component: object, callback: str, kwargs: dict) -> None:
        """Выполнить указанное действие."""
        try:
            Aggregator._callbacks[callback](component, **kwargs)
        except KeyError:
            print('Такого действия не существует!')

    @classmethod
    def on(self, component: object, **kwargs) -> None:
        """Включить пины у переданных компонентов.

        Параметры:
          :param component: — кортеж из произвольного количества компонентов.
        """
        component.on(**kwargs)

    @classmethod
    def off(self, component: object, **kwargs) -> None:
        """Выключить пины у переданных компонентов.

        Параметры:
          :param component: — кортеж из произвольного количества компонентов.
        """
        component.off(**kwargs)

    @classmethod
    def toggle(self, component: object, **kwargs) -> None:
        """Изменить состояние пинов переданных компонентов на противоположное.

        Параметры:
          :param component: — кортеж из произвольного количества компонентов.
        """
        component.toggle(**kwargs)

    @classmethod
    def set_state(self, component: object, new_state: Any) -> None:
        """Установить новое значение состояния компоненту.

        Параметры:
          :param component: — объект компонента;
          :param new_state: — новое состояние компонента.
        """
        component.state = new_state

    @classmethod
    def reboot(self, device, conn: sqlite3.connect) -> None:
        """Перезагрузить устройство. Перезагрузка несколько раз подряд не
        позволяется."""

        if self.is_rebootable(self, conn):
            notify(device, 'reboot', swap=True, type_='status')
            # subprocess.run('/usr/bin/sudo reboot', shell=True)
        else:
            print('Кулдаун не завершён. Перезагрузка прямо сейчас невозможна.')

    def is_rebootable(self, conn: sqlite3.connect) -> None:
        """Перезагрузить устройство. Перезагрузка несколько раз подряд не
        позволяется."""
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp
            FROM status_archive
            WHERE state=reboot
            LIMIT 1;
            ''')
        timestamp = cursor.fetchone()

        print(timestamp)
        print(dt.timestamp() - timestamp)

        return timestamp and dt.timestamp() - timestamp < 60
