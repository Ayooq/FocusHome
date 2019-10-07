import asyncio
import datetime as dt
import json
import operator
import shelve
import subprocess
# from concurrent.futures import ThreadPoolExecutor
# from functools import partial
from time import sleep
from typing import Any, Callable, Dict, List, NoReturn, Tuple, Type, Union

import yaml

from ..utils import BACKUP_FILE, COMMANDS_FILE, CONFIG_FILE
from ..utils.db_tools import fill_table
from ..utils.messaging import notify
from .parse import Parser

# from celery.app import app_or_default

ShelveDB = shelve.DbfilenameShelf


class CommandsRegistry:

    @staticmethod
    def set_value(component: Type[object], value: str) -> None:
        """Установить компоненту переданное значение.

        :param component: экземпляр объекта компонента
        :type component: object
        :param value: новое значение
        :type value: str
        """
        component.state = value

    @classmethod
    def reboot(cls, device: Type[object], **kwargs) -> NoReturn:
        """Перезагрузить устройство.

        Перезагрузка с интервалом меньше, чем в минуту, не позволяется.

        :param device: экземпляр объекта устройства
        :type device: object
        """
        if cls.is_rebootable(device.db):
            notify(device, 'fake reboot', no_repr=True,
                   report_type='status', local_only=True)
            # notify(device, 'reboot', no_repr=True, report_type='status')
            # subprocess.run('/usr/bin/sudo reboot', shell=True)
        else:
            print('Перезагрузка чаще, чем в установленный промежуток времени, \
                не разрешена!')

    @staticmethod
    def is_rebootable(conn: Type[object]) -> bool:
        """Проверить готовность устройства к перезагрузке.

        :param conn: экземпляр объекта соединения с БД
        :type conn: object

        :return: результат проверки
        :rtype: bool
        """
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp
            FROM status_archive
            WHERE state="reboot"
            LIMIT 1;
            ''')
        timestamp = cursor.fetchone()

        if not timestamp:
            return True

        timestamp = dt.datetime.strptime(timestamp[0], '%Y-%m-%d %H:%M:%S.%f')
        timediff = dt.datetime.now() - timestamp

        return timediff < dt.timedelta(seconds=60)

    @staticmethod
    def on(component: Type[object], **kwargs) -> None:
        r"""Включить пин компонента.

        :param component: экземпляр объекта компонента
        :type component: object
        :param **kwargs: опциональные именованные аргументы
        :type **kwargs: dict
        """
        component.on(**kwargs)

    @staticmethod
    def off(component: Type[object], **kwargs) -> None:
        r"""Выключить пин компонента.

        :param component: экземпляр объекта компонента
        :type component: object
        :param **kwargs: опциональные именованные аргументы
        :type **kwargs: dict
        """
        component.off(**kwargs)

    @staticmethod
    def toggle(component: Type[object], **kwargs) -> None:
        r"""Изменить состояние пина компонента на противоположное.

        :param component: экземпляр объекта компонента
        :type component: object
        :param **kwargs: опциональные именованные аргументы
        :type **kwargs: dict
        """
        component.toggle(**kwargs)

    @staticmethod
    def set_state(
            component: Type[object], value: Union[int, float, str]) -> None:
        """Установить новое значение состояния компоненту.

        :param component: экземпляр объекта компонента
        :type component: object
        :param value: новое состояние компонента
        :type value: int or float or str
        """
        component.state = value

    @staticmethod
    async def report_at_intervals(
            component: Type[object], pending_time: int) -> NoReturn:
        """Уведомлять о состоянии компонента c заданной периодичностью.

        :param component: экземпляр объекта компонента
        :type component: object
        :param pending_time: время простоя перед оповещением
        :type pending_time: int
        """
        await asyncio.sleep(pending_time)
        notify(component, component.state, report_type='info')

    @classmethod
    async def watch_state(cls, component: Type[object]) -> NoReturn:
        """Наблюдать за состоянием компонента.

        :param component: экземпляр объекта компонента
        :type component: object
        """
        if await cls.is_exceeded(component):
            notify(component, component.state, report_type='warning')
        elif await cls.is_back_to_normal(component):
            notify(component, component.state)

    @staticmethod
    async def is_exceeded(component: Type[object]) -> bool:
        """Проверка состояния компонента на несоответствие установленной норме.

        :param component: экземпляр объекта компонента
        :type component: object

        :return: результат проверки на превышение порога допустимых значений
        :rtype: bool
        """
        return component.is_active and not component.exceeded

    @staticmethod
    async def is_back_to_normal(component: Type[object]) -> bool:
        """Проверка состояния компонента на возвращение к установленной норме.

        :param component: экземпляр объекта компонента
        :type component: object

        :return: результат проверки на возврат показателей в норму
        :rtype: bool
        """
        return component.exceeded and not component.is_active


# class AsyncLoop(ThreadPoolExecutor):
#     """Петля для асинхронного исполнения синхронных команд"""

#     def __init__(self, nthreads=1):
#         self._ex = ThreadPoolExecutor(nthreads)
#         self._loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(self._loop)

#     def __call__(self, f, *args, **kwargs):
#         return self._loop.run_in_executor(self._ex, partial(f, *args, **kwargs))


class Handler:
    """Обработчик принимаемых инструкций.

    :param device: экземпляр объекта устройства
    :type device: focus.back.FocusPro
    """

    def __init__(self, device: Type[object]) -> None:
        self.device = device
        self.routines = self._get_routines()

        for i, (k, v) in enumerate(self.routines.items(), start=1):
            print(f'Рутина {i}) {k}: {v}')

        # Словарь последних отправленных сообщений от имени каждого компонента:
        self.sended_messages = {}

        # Регистрация обработчиков событий:
        msg = 'регистрирую подписчиков...'
        notify(device, msg, no_repr=True, local_only=True)

        for group in (self.device.hardware).values():
            self._set_subscriptions(
                device, group, blink=self._blink, pub=self._publish)

        self._set_subscriptions(device, blink=self._blink, pub=self._publish)

    def _get_routines(self) -> dict:
        with shelve.open(COMMANDS_FILE) as db:
            return dict(db.items())

    def handle(self, instructions: Dict[str, List[tuple]]) -> None:
        """Обработать принятые инструкции.

        Рутины добавляются в пул асинхронно исполняемых сопрограмм, команды
        выполняются синхронно в порядке установленной очереди.

        :param instructions: словарь исполняемых инструкций
        :type instructions: dict
        """
        for i in instructions.get('routines'):
            routine_id, actions, conditions, components_objects = i

            for co in components_objects:
                co.reporter.register(routine_id, self._eval_and_exec,
                                     routine_id, actions, conditions)

        for command_id, actions in instructions.get('commands'):
            self.execute_command(command_id, actions)

    def execute_command(
        self,
        command_id: str,
        actions: Tuple[str, str, Dict[str, str]]
    ) -> None:
        """Выполнить команду.

        Если команда уже содержится в реестре исполняемых макросов,
        найти её по ключу и выполнить. Иначе исполнить каждое указанное в ней
        действие в порядке установленной очерёдности и записать в реестр как
        новый макрос.

        :param command_id: идентификатор команды
        :type command_id: str
        :param actions: последовательность действий для исполнения команды
        :type actions: list[list]
        """
        try:
            print('command id:', command_id)
            self.run_macros(self.routines, command_id)
        except KeyError:
            print('failed to run macros, performing a new set of actions...')
            macros = []

            for index, action in enumerate(actions, start=1):
                # target, action, kwargs = action
                print(f'action {index}:', action)
                macros.append(action)

                if index == len(actions):
                    with shelve.open(COMMANDS_FILE) as db:
                        print('macros:', macros)
                        db[command_id] = macros
                        print('saved a new macros!')

                self.perform_action(*action)

            # Если программа продолжает работать, обновить словарь рутин:
            self.routines[command_id] = macros

    def run_macros(self, routines: dict, command_id: str) -> None:
        print('trying to run macros...')
        for id_, macros in routines.items():
            print('macros:', f'<{id_}: {macros}>')

        macros = routines[command_id]

        for index, action in enumerate(macros, start=1):
            print(f'action {index}:', action)
            self.perform_action(*action)

    def perform_action(self, target: str, action: str, kwargs: dict) -> Any:
        """Выполнить действие.

        :param target: цель совершаемого действия
        :type target: str
        :param action: название функции обработки указанного действия
        :type action: str
        :param kwargs: передаваемые обработчику именованные аргументы
        :type kwargs: dict

        :return: результат выполненного действия
        :rtype: Any
        """
        cmd = getattr(CommandsRegistry, action)
        print('performing action...')
        print('command:', cmd)
        target = self.device if target == 'self' else Parser._get_component(
            target, self.device.hardware)

        print('target:', target)
        print('kwargs:', kwargs)

        return cmd(target, **kwargs)

    def run_forever(self, routines: List[tuple]) -> NoReturn:
        """Запустить бесконечный цикл исполнения сопрограмм в отдельном потоке.

        Параметры:
          :param routines: — список доступных для исполнения рутин.
        """
        ...

    def apply_config(self, old_data: dict, new_data: dict) -> None:
        """Применить новые настройки конфигурации, заданные пользователем.

        Сделать резервную копию текущей конфигурации и записать новые настройки
        в указанные файлы.

        :param old_data: текущая конфигурация
        :type old_data: dict
        :param new_data: новые данные для конфигурации
        :type new_data: dict
        """
        self._write_yaml(
            old_data, BACKUP_FILE, default_flow_style=False, sort_keys=False)

        units, complects = {}, {}
        family, id_, pin, params = 0, 1, 2, 3

        for i in new_data.get('units'):
            if i[family].startswith('c'):
                # Настройка составных компонентов:
                component = self.prepare_data(complects, i, family, id_)
            else:
                # Настройка одиночных компонентов:
                component = self.prepare_data(units, i, family, id_)

            self.setup_component(component, i, pin, params)

        new_config = {
            'device': new_data.get('device'),
            'snmp': new_data.get('snmp'),
            'mqtt': old_data.get('mqtt'),
            'units': units,
            'complects': complects,
        }
        print('Новая конфигурация:', new_config)

        self._write_yaml(
            new_config, CONFIG_FILE, default_flow_style=False, sort_keys=False)

    @staticmethod
    def prepare_data(
            group: dict,
            component: list,
            family: int,
            id_: int
    ) -> dict:
        """Подготовить к установке компонент данной группы.

        :param group: группа настроенных компонентов
        :type group: dict
        :param component: настраиваемый компонент
        :type component: List[str, str, int, dict]
        :param family: индекс семейства компонента
        :type family: int
        :param id_: индекс кодового идентификатора компонента
        :type id_: int

        :return: незаполненный словарь данных компонента
        :rtype: dict
        """
        component_data = {component[id_]: {}}

        if component[family] not in group:
            group[component[family]] = component_data
        else:
            group[component[family]].update(component_data)

        return group[component[family]][component[id_]]

    @staticmethod
    def setup_component(
            data: dict,
            component: list,
            pin: int,
            params: int,
    ) -> None:
        """Установить данные компоненту для его последующей инициализации.

        :param data: незаполненный словарь данных компонента
        :type data: dict
        :param component: настраиваемый компонент
        :type component: List[str, str, int, dict]
        :param pin: индекс ПИНа компонента
        :type pin: int
        :param params: индекс опциональных параметров компонента
        :type params: int
        """
        try:
            data = component[params]
        except ValueError:
            print(component[params])
            print('Для правильной настройки необходим словарь!')

            raise

        if component[pin] > 0:
            data['pin'] = component[pin]

    def _write_yaml(self, config: dict, file: str, **kwargs) -> None:
        with open(file, 'w') as f:
            yaml.safe_dump(config, f, **kwargs)

    def _set_subscriptions(
            self,
            device: Type[object],
            group: dict = None,
            **kwargs: Callable
    ) -> None:
        if not group:
            for subscriber, callback in kwargs.items():
                device.reporter.register(subscriber, callback, device)

            notify(device, 'готово.', no_repr=True, local_only=True)

            return

        for family in group.values():
            for component in family.values():
                for subscriber, callback in kwargs.items():
                    component.reporter.register(subscriber, callback, device)

                notify(component, 'готово.', local_only=True)

    def _blink(self, report: Type[dict], device: Type[object]) -> None:
        """Осуществлять световую индикацию при регистрации событий.

        Индикация производится следующим образом:
        1) event — светодиод включается на секунду, затем выключается,
        однократно;
        2) info/status — светодиод включается на секунду, отключается на одну,
        дважды;
        3) warning — светодиод включается на две секунды, отключается на одну,
        трижды;
        4) error — светодиод включается на три секунды, выключается на одну,
        трижды.

        :param report: экземпляр отчёта
        :type report: dict
        :param device: экземпляр объекта устройства
        :type device: focus.back.FocusPro
        """
        msg_type = report['type']

        if msg_type == 'event':
            device.indicators['led2'].blink(1, 1, 1)
        elif msg_type in ('info', 'status'):
            device.indicators['led2'].blink(1, 1, 2)
        elif msg_type == 'warning':
            device.indicators['led2'].blink(2, 1, 3)
        elif msg_type == 'error':
            device.indicators['led2'].blink(3, 1, 3)

    def _publish(self, report: Type[dict], device: Type[object]) -> None:
        msg_body = report['message']
        unit = 'self' if report['from'] == device.id else report['from']

        if self.is_duplicate(unit, msg_body):
            return

        payload = self._form_payload(report, device, unit, msg_body)
        pub_data = self._form_pub_data(report, device, unit, payload)

        device.indicators['led1'].on()
        device.client.publish(**pub_data)
        self.sended_messages[unit] = msg_body
        device.indicators['led1'].off()

    def is_duplicate(self, unit: str, msg: Union[int, float, str]) -> bool:
        """Проверить, является ли данное сообщение дубликатом последнего
        отправленного указанным компонентом.

        :param unit: наименование компонента
        :type unit: str
        :param msg: тело сообщения
        :type msg: int or float or str

        :return: результат проверки
        :rtype: bool
        """
        return msg == self.sended_messages.get(unit)

    def _form_payload(
        self,
        report: Type[dict],
        device: Type[object],
        unit: str,
        msg_body: Union[int, str, float]
    ) -> str:
        timestamp = dt.datetime.now().isoformat(sep=' ')
        msg_type = report['type']

        cursor = device.db.cursor()
        tables_set = {'events'}
        tabledata = [timestamp, msg_type, unit, str(msg_body)]

        fill_table(device.db, cursor, tables_set, tabledata)

        tables_set.clear()
        tables_set.update({'status', 'status_archive'})
        tabledata.pop(1)

        fill_table(device.db, cursor, tables_set, tabledata)

        return json.dumps((timestamp, msg_type, msg_body))

    def _form_pub_data(
        self,
        report: Type[dict],
        device: Type[object],
        unit: str,
        payload: str
    ) -> Dict[str, Union[str, int, bool]]:
        topic = '/'.join([device.id, 'report', unit])
        qos = report['qos']
        retain = report['retain']

        return {
            'topic': topic,
            'payload': payload,
            'qos': qos,
            'retain': retain,
        }

    def _eval_and_exec(
        self,
        report: Type[dict],
        routine_id: str,
        actions: List[Tuple[str, str, Dict[str, str]]],
        conditions: str,
    ) -> None:
        expr = []

        for c in conditions.split():
            if c.startswith('$'):
                op, unit, val = c.split(':')
                unit_state = Parser._get_component(
                    unit, self.device.hardware).state
                expr.append(f'{op[1:]}({unit_state}, {val})')
            else:
                expr.append(c)

        print('Expr:', expr)
        res = eval(' '.join(expr))
        print('Result:', res)

        if res:
            self.execute_command(routine_id, actions)

    # def run(self, component: object, command: str, **kwargs) -> None:
    #     """Выполнить указанную команду.

    #     Параметры:
    #       :param component: — объект компонента;
    #       :param command: — строковый идентификатор команды;
    #       :param kwargs: — опциональный словарь именованных аргументов.
    #     """
    #     with shelve.open(ROUTINES_FILE) as db:
    #         try:
    #             db[command](component, **kwargs)
    #         except KeyError:
    #             print('Такой команды нет!')

    # async def gather(self, *coros: Awaitable[Any]) -> Awaitable:
    #     """Добавить сопрограммы на исполнение в петлю событий.

    #     Параметры:
    #       :param coros: — кортеж из произвольного количества сопрограмм для
    #     исполнения.
    #     """
    #     return await asyncio.gather(*coros)

    # @classmethod
    # async def sleep_for(self, sec: int) -> None:
    #     """Отложить исполнение сопрограммы на указанный период времени.

    #     Параметры:
    #       :param sec: — количество секунд, определяющее величину задержки.
    #     """
    #     await asyncio.sleep(sec)

    # def register_routines(
    #         self, *routines: Tuple[int, Callable, list]) -> None:
    #     """Занести полученные рутины в специализированную БД.

    #     БД реализует интерфейс словаря, в который записываются данные вида
    #     <ключ: значение>. Каждому новому ключу присваивается свой обработчик
    #     для конкретной рутины. Аргументы на данном этапе не передаются.

    #     Параметры:
    #         :param routines: — произвольное количество рутин в виде кортежей
    #     из трёх элементов (числовой идентификатор для использования в качестве
    #     ключа, объект функции-обработчика рутины, выступающий в роли значения
    #     по ключу, и список аргументов для исполнения конкретной рутины).
    #     """
    #     with shelve.open(COMMANDS_FILE) as db:
    #         for i in routines:
    #             key, handler, _ = i
    #             db[key] = handler
