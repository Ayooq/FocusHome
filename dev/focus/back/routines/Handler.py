import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Awaitable, Callable, Tuple

import yaml

from ..utils import BACKUP_FILE, CONFIG_FILE


class Handler:
    """Обработчик асинхронных команд.

    Методы:
      :meth __init__(self): — конструктор экземпляров класса;
      :meth write_yaml: — записать в указанный файл .yml содержимое
    переданного словаря;
      :meth apply_config: — применить новые настройки конфигурации устройства;
      :meth dispatch(self, *coros): — распределить поступающие команды;
      :meth run(self, *coros): — дождаться выполнения сопрограмм и вернуть
    результат их выполнения;
      :meth run_forever: — запустить выполнение сопрограмм в бесконечном цикле;
      :async meth gather: — вернуть Future, содержащий результаты выполнения
    переданных сопрограмм;
      :async meth sleep_for: — отложить исполнение сопрограммы на указанное
    количество секунд.
    """

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def write_yaml(self, config: dict, file: str, **kwargs) -> None:
        with open(file, 'w') as f:
            yaml.dump(config, f, **kwargs)

    def apply_config(self, old_data: dict, new_data: dict) -> None:
        """Применить новые настройки конфигурации, заданные пользователем.

        Сделать резервную копию текущей конфигурации и записать новые настройки
        в указанные файлы.

        Параметры:
          :param old_data: — объект словаря с текущей конфигурацией;
          :param new_data: — объект словаря с новой конфигурацией.
        """

        self.write_yaml(old_data, BACKUP_FILE)

        units, complects = {}, {}
        family, unit, pin, params = 0, 1, 2, 3

        # Настройка одиночных компонентов:
        for i in new_data.get('units'):
            if i[family] not in units:
                units[i[family]] = {i[unit]: {}}

            unit_data = units[i[family]].get(i[unit], {})

            if i[pin] > 0:
                unit_data['pin'] = i[pin]

            try:
                unit_data.update(i[params])
            except IndexError:
                pass

        # Настройка составных компонентов:
        couts = units.pop('couts')
        complects['couts'] = {
            'cmp1': {
                'out': couts.get('out1'),
                'cnt': couts.get('cnt1'),
            },
            'cmp2': {
                'out': couts.get('out2'),
                'cnt': couts.get('cnt2'),
            },
            'cmp3': {
                'out': couts.get('out3'),
                'cnt': couts.get('cnt3'),
            },
            'cmp4': {
                'out': couts.get('out4'),
                'cnt': couts.get('cnt4'),
            },
        }

        new_config = {
            'device': new_data.get('device'),
            'snmp': new_data.get('snmp'),
            'mqtt': old_data.get('mqtt'),
            'units': units,
            'complects': complects,
        }

        self.write_yaml(new_config, CONFIG_FILE, default_flow_style=False)

    def handle(
            self,
            *coros: Tuple[int, bool, Awaitable, Any],
            max_workers=3
    ) -> None:
        """Асинхронно обработать сопрограммы.

        Параметры:
          :param coros: — сопрограммы для обработки. Каждая сопрограмма
        представляет собой кортеж со следующими элементами:
          1) время, спустя которое должна запуститься команда;
          2) флаг повторного вызова команды;
          3) команда для выполнения;
          4) аргументы, передаваемые с командой;
          :param max_workers: — целое число, указывающее предельно допустимое
        количество служб внутри отдельного потока.
        """

        for coro in coros:
            delta = coro[0]
            repeat = coro[1]
            action = coro[2]
            args = coro[3:] if coro[-1] != action else []

            if delta:
                self.run(self.sleep_for(delta))

            if repeat:
                self.run_forever(action(*args))

            self.run(action(*args))

    def run(self, *coros: Awaitable[Any]) -> Any:
        """Выполнить сопрограммы в отдельном потоке.

        Параметры:
          :param coros: — кортеж из произвольного количества сопрограмм для
        исполнения.
        """
        return self.loop.run_until_complete(self.gather(*coros))

    def run_forever(self, *coros: Awaitable[Any]) -> Any:
        """Запустить бесконечный цикл исполнения сопрограмм в отдельном потоке.

        Параметры:
          :param coros: — кортеж из произвольного количества сопрограмм для
        исполнения.
        """
        return self.loop.run_forever(self.gather(*coros))

    async def gather(self, *coros: Awaitable[Any]) -> Awaitable:
        """Добавить сопрограммы на исполнение в петлю событий.

        Параметры:
          :param coros: — кортеж из произвольного количества сопрограмм для
        исполнения.
        """
        return await asyncio.gather(*coros)

    @classmethod
    async def sleep_for(self, sec: int) -> None:
        """Отложить исполнение сопрограммы на указанный период времени.

        Параметры:
          :param sec: — количество секунд, определяющее величину задержки.
        """
        await asyncio.sleep(sec)

# def run(coroutine):
#     return asyncio.run(coroutine)


# async def main():
#     with shelve.open(ROUTINES_FILE) as db:
#         async for routine in db:
#             await worker()
