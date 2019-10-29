import asyncio
import datetime as dt
import json
import operator
import shelve
import subprocess
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from gzip import compress
from time import sleep
from typing import (Any, Callable, Dict, Iterator, List,
                    NoReturn, Tuple, Type, Union)

import yaml
from pysnmp import hlapi

from ..utils import BACKUP_FILE, COMMANDS_FILE, CONFIG_FILE
from ..utils.db_tools import fill_tables
from ..utils.messaging import notify
from .parse import Parser

ShelveDB = shelve.DbfilenameShelf


class CommandsRegistry:

    # SNMP:
    @classmethod
    def snmp_send_data(
            cls,
            device: Type[object],
            target: str,
            oids: List[str],
            credentials: Union[hlapi.CommunityData, hlapi.UsmUserData],
            engine: hlapi.SnmpEngine = None,
            context: hlapi.ContextData = None,
            port: int = 161,
            count: Union[int, str] = 1,
            start_from: Union[int, None] = None,
    ) -> None:
        """Отправить посреднику данные агента в базе управляющей информации.

        :param device: экземпляр объекта устройства
        :type device: focus.back.FocusPro
        :param target: IP-адрес удалённого устройства
        :type target: str
        :param oids: идентификаторы искомых объектов
        :type oids: list[str]
        :param credentials: набор полномочий для аутентификации сессии
        :type credentials: hlapi.CommunityData or hlapi.UsmUserData
        :param engine: движок SNMP, по умолчанию None
        :type engine: hlapi.SnmpEngine
        :param context: контекстные данные, по умолчанию None
        :type context: hlapi.ContextData
        :param port: порт подключения к удалённому устройству, по умолчанию 161
        :type port: int
        :param count: количество экземпляров объекта, по умолчанию 1
        :type count: int
        :param start_from: номер узла, с которого необходимо начать выборку
        по умолчанию None
        :type start_from: int or None
        """
        engine = engine or device.config['snmp']['engine']
        context = context or device.config['snmp']['context']
        args = device, target, oids, credentials, engine, context, port

        if start_from is not None:
            if isinstance(count, int) and count > 1:
                print('get bulk')
                snmp_data = cls.snmp_get_bulk(*args, count, start_from)
            else:
                print('get bulk auto')
                snmp_data = cls.snmp_get_bulk_auto(*args, count, start_from)
        else:
            print('get data')
            snmp_data = cls.snmp_get_data(*args)

        snmp_data = json.dumps(snmp_data)
        gzip_bytes = compress(snmp_data.encode())

        mqtt_settings = {'qos': 1, 'retain': False}
        pub_data = Handler._form_pub_data(
            device, mqtt_settings, 'self', gzip_bytes, topic='snmp')

        device.indicators['led1'].on()
        device.client.publish(**pub_data)
        device.indicators['led1'].off()

    @classmethod
    def snmp_get_data(
            cls,
            device: Type[object],
            target: str,
            oids: List[str],
            credentials: Union[hlapi.CommunityData, hlapi.UsmUserData],
            engine: hlapi.SnmpEngine,
            context: hlapi.ContextData,
            port: int,
    ) -> str:
        """Получить значение отдельного объекта в базе управляющей информации.

        :param device: экземпляр объекта устройства
        :type device: focus.back.FocusPro
        :param target: IP-адрес удалённого устройства
        :type target: str
        :param oids: идентификаторы искомых объектов
        :type oids: list[str]
        :param credentials: набор полномочий для аутентификации сессии
        :type credentials: hlapi.CommunityData or hlapi.UsmUserData
        :param engine: движок SNMP
        :type engine: hlapi.SnmpEngine
        :param context: контекстные данные
        :type context: hlapi.ContextData
        :param port: порт подключения к удалённому устройству
        :type port: int

        :raises RuntimeError: ошибка обработки SNMP сообщения

        :return: данные объекта в MIB в формате JSON
        :rtype: str
        """
        snmp_handler = hlapi.getCmd(
            engine,
            credentials,
            hlapi.UdpTransportTarget((target, port)),
            context,
            *cls.construct_object_types(oids)
        )

        return cls.fetch(device, snmp_handler, 1)[0]

    @classmethod
    def snmp_get_bulk(
            cls,
            device: Type[object],
            target: str,
            oids: List[str],
            credentials: Union[hlapi.CommunityData, hlapi.UsmUserData],
            engine: hlapi.SnmpEngine,
            context: hlapi.ContextData,
            port: int,
            count: int,
            start_from: str,
    ) -> str:
        """Получить значения множества экземпляров объекта в MIB.

        Точное количество данных определяется параметром :param count:,
        проход по древу объекта начинается с узла, установленного в параметре
        :param count_from:.

        :param device: экземпляр объекта устройства
        :type device: focus.back.FocusPro
        :param target: IP-адрес удалённого устройства
        :type target: str
        :param oids: идентификаторы искомых объектов
        :type oids: list[str]
        :param credentials: набор полномочий для аутентификации сессии
        :type credentials: hlapi.CommunityData or hlapi.UsmUserData
        :param engine: движок SNMP
        :type engine: hlapi.SnmpEngine
        :param context: контекстные данные
        :type context: hlapi.ContextData
        :param port: порт подключения к удалённому устройству
        :type port: int
        :param count: количество экземпляров объекта
        :type count: int
        :param start_from: номер узла, с которого необходимо начать выборку
        :type start_from: int

        :raises RuntimeError: ошибка обработки SNMP сообщения

        :return: данные объекта в MIB в формате JSON
        :rtype: str
        """
        snmp_handler = hlapi.bulkCmd(
            engine,
            credentials,
            hlapi.UdpTransportTarget((target, port)),
            context,
            start_from, count,
            *cls.construct_object_types(oids)
        )

        return cls.fetch(device, snmp_handler, count)

    @classmethod
    def snmp_get_bulk_auto(
            cls,
            device: Type[object],
            target: str,
            oids: List[str],
            credentials: Union[hlapi.CommunityData, hlapi.UsmUserData],
            engine: hlapi.SnmpEngine,
            context: hlapi.ContextData,
            port: int,
            count_oid: int,
            start_from: str,
    ) -> str:
        """Получить значения множества экземпляров объекта в MIB.

        Количество экземпляров определяется с помощью специальной записи в узле,
        указанном в параметре :param count_oid:.

        :param device: экземпляр объекта устройства
        :type device: focus.back.FocusPro
        :param target: IP или адрес удалённого устройства
        :type target: str
        :param oids: идентификаторы искомых объектов
        :type oids: list[str]
        :param credentials: набор полномочий для аутентификации сессии
        :type credentials: hlapi.CommunityData or hlapi.UsmUserData
        :param engine: движок SNMP
        :type engine: hlapi.SnmpEngine
        :param context: контекстные данные
        :type context: hlapi.ContextData
        :param port: порт подключения к удалённому устройству
        :type port: int
        :param count_oid: идентификатор количества итераций объектов
        :type count_oid: str
        :param start_from: номер узла, с которого необходимо начать выборку,
        :type start_from: int

        :raises RuntimeError: ошибка обработки SNMP сообщения

        :return: данные объекта в MIB в формате JSON
        :rtype: str
        """
        count = cls.snmp_get_data(device, target, [count_oid], credentials,
                                  engine, context, port)[count_oid]
        print('COUNT:', count)

        return cls.snmp_get_bulk(device, target, oids, credentials, engine,
                                 context, port, count, start_from)

    @staticmethod
    def construct_object_types(list_of_oids: List[str]) -> List[str]:
        """Сконструировать специальные объекты для выборки данных.

        :param list_of_oids: идентификаторы объектов
        :type list_of_oids: list[str]

        :return: объекты для передачи в функцию выборки
        :rtype: list[str]
        """
        return [hlapi.ObjectType(
                hlapi.ObjectIdentity(oid)) for oid in list_of_oids]

    @classmethod
    def fetch(
        cls,
        device: Type[object],
        snmp_handler: Iterator,
        count: int,
    ) -> List[dict]:
        """Выбрать данные, возвращаемые обработчиком GET запросов.

        :param device: экземпляр объекта устройства
        :type device: focus.back.FocusPro
        :param snmp_handler: обработчик SNMP
        :type snmp_handler: generator
        :param count: количество запросов данных
        :type count: int

        :raises RuntimeError: ошибка обработки SNMP сообщения

        :return: результаты запроса
        :rtype: list[dict]
        """
        result = []

        for i in range(count):
            try:
                err_indication, err_status, _, var_binds = next(snmp_handler)

                if err_indication or err_status:
                    msg = 'ошибка обработки SNMP сообщения'
                    notify(device, msg, no_repr=True, report_type='error')

                    raise RuntimeError(
                        f'Ошибка в итерации цикла №{i}: {err_indication}')

                items = {}

                for var_bind in var_binds:
                    k, v = var_bind
                    items[str(k)] = cls.cast(v)

                result.append(items)
            except StopIteration:
                break

        return result

    @staticmethod
    def cast(value: Any) -> Union[int, float, str]:
        """Привести значение к определённому типу.

        Приведение осуществляется в следующем порядке:
        1) привести к целому числу, иначе
        2) привести к числу с плавающей точкой, иначе
        3) привести к строке.

        Если приведение к вышеописанным типам невозможно, вернуть первоначальное
        значение.

        :param value: приводимое значение
        :type value: Any

        :return: приведённое либо первоначальное значение
        :rtype: int or float or str or Any
        """
        try:
            return int(value)
        except (ValueError, TypeError):
            try:
                return float(value)
            except (ValueError, TypeError):
                try:
                    return str(value)
                except (ValueError, TypeError):
                    pass

        return value

    # Синхронные команды:
    @classmethod
    def reboot(cls, device: Type[object], **kwargs) -> NoReturn:
        """Перезагрузить устройство.

        Перезагрузка с интервалом меньше, чем в две минуты, не позволяется.
        """
        if cls.is_rebootable(device.db):
            # notify(device, 'fake reboot', no_repr=True,
            #       report_type='status', local_only=True)
            notify(device, 'reboot', no_repr=True, report_type='status')
            subprocess.run('/usr/bin/sudo reboot', shell=True)
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

        return timediff < dt.timedelta(seconds=120)

    @staticmethod
    def on(components: list, **kwargs) -> None:
        r"""Включить пин у каждого переданного компонента.

        :param component: экземпляр объекта компонента
        :type component: object
        :param **kwargs: опциональные именованные аргументы
        :type **kwargs: dict
        """
        for component in components:
            component.on(**kwargs)

    @staticmethod
    def off(components: list, **kwargs) -> None:
        r"""Выключить пин у каждого переданного компонента.

        :param component: экземпляр объекта компонента
        :type component: object
        :param **kwargs: опциональные именованные аргументы
        :type **kwargs: dict
        """
        for component in components:
            component.off(**kwargs)

    @staticmethod
    def toggle(components: list, **kwargs) -> None:
        r"""Переключить пин у каждого переданного компонента.

        :param component: экземпляр объекта компонента
        :type component: object
        :param **kwargs: опциональные именованные аргументы
        :type **kwargs: dict
        """
        for component in components:
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

    # Асинхронные команды:
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


class AsyncLoop(ThreadPoolExecutor):
    """Петля для асинхронного исполнения синхронных команд"""

    def __init__(self, nthreads=1):
        self._ex = ThreadPoolExecutor(nthreads)
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

    def __call__(self, f, *args, **kwargs):
        return self._loop.run_in_executor(self._ex, partial(f, *args, **kwargs))

    def run(self, command: str, components: list, **kwargs) -> None:
        """Выполнить указанную команду.

        Параметры:
          :param command: — строковый идентификатор команды;
          :param component: — объект компонента;
          :param kwargs: — опциональный словарь именованных аргументов.
        """
        with shelve.open(COMMANDS_FILE) as db:
            try:
                for c in components:
                    db[command](c, **kwargs)
            except KeyError:
                print('Такой команды нет!')

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


class Handler:
    """Обработчик принимаемых инструкций.

    :param device: экземпляр объекта устройства
    :type device: focus.back.FocusPro
    """

    def __init__(self, device: Type[object]) -> None:
        self.device = device
        self.async_ = AsyncLoop()
        self.routines = self._get_routines()

        for i, (k, v) in enumerate(self.routines.items(), start=1):
            print(f'Рутина {i}) {k}: {v}')

        # Словарь последних отправленных сообщений от имени каждого компонента:
        self.sended_messages = {}

        # Регистрация обработчиков событий:
        msg = 'регистрирую подписчиков...'
        notify(self.device, msg, no_repr=True, local_only=True)

        for group in (self.device.hardware).values():
            self._set_subscriptions(
                group, blink=self._blink, pub=self._publish)

        self._set_subscriptions(blink=self._blink, pub=self._publish)

    def _get_routines(self) -> dict:
        with shelve.open(COMMANDS_FILE) as db:
            return dict(db.items())

    def handle(self, instructions: Dict[str, List[tuple]]) -> None:
        """Обработать принятые инструкции.

        Рутинам присваиваются слушатели изменения состояния. При наступлении
        всех обозначенных условий рутина исполняется обработчиком. Команды
        выполняются сразу в порядке установленной очереди.

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

    def execute_command(self, command_id: str, actions: list) -> None:
        """Выполнить команду.

        Если команда уже содержится в реестре исполняемых макросов,
        найти её по ключу и выполнить. Иначе исполнить каждое указанное в ней
        действие в порядке установленной очерёдности и записать в реестр как
        новый макрос.

        :param command_id: идентификатор команды
        :type command_id: str
        :param actions: последовательность действий для исполнения команды
        :type actions: list
        """
        try:
            print('command id:', command_id)
            self.run_macro(self.routines, command_id)
        except KeyError:
            print('failed to run macro, performing a new set of actions...')
            macro = []

            for index, action in enumerate(actions, start=1):
                # target, command, kwargs = action
                print(f'action {index}:', action)
                macro.append(action)

                if index == len(actions):
                    self.save_macro(command_id, macro)

                self.perform_action(*action)

            # Если программа продолжает работать, обновить словарь рутин:
            self.routines[command_id] = macro

    def run_macro(self, routines: dict, command_id: str) -> None:
        print('trying to run macro...')
        for id_, macro in routines.items():
            print('macro:', f'<{id_}: {macro}>')

        macro = routines[command_id]

        for index, action in enumerate(macro, start=1):
            print(f'action {index}:', *action)
            self.perform_action(*action)

    @staticmethod
    def save_macro(command_id: str, macro: list) -> None:
        with shelve.open(COMMANDS_FILE) as db:
            print('macro:', macro)
            db[command_id] = macro
            print('saved a new macro!')

    def perform_action(
            self,
            target: Union[str, list],
            action: str,
            async_: bool,
            kwargs: dict,
    ) -> Any:
        """Выполнить действие.

        :param target: один или несколько компонентов, к которым необходимо
        применить действие
        :type target: str or list
        :param action: название функции обработки указанного действия
        :type action: str
        :param async_: флаг, обозначающий синхронность/асинхронность действия
        :type async_: bool
        :param kwargs: именованные аргументы, передаваемые обработчику
        :type kwargs: dict

        :return: результат выполненного действия
        :rtype: Any
        """
        cmd = getattr(CommandsRegistry, action)
        print('performing action...')

        if isinstance(target, str):
            target = self.id_to_object(target)

            return cmd(target, **kwargs)

        for i, c in enumerate(target):
            target[i] = self.id_to_object(c)

        print('components:', target)
        print('kwargs:', kwargs)

        if async_:
            self.async_.run(cmd, target, **kwargs)
        else:
            return cmd(target, **kwargs)

    def id_to_object(self, id_: str):
        """Преобразовать строковый идентификатор в экземпляр объекта компонента.

        :param id_: строковый идентификатор компонента
        :type id_: str

        :return: экземпляр объекта устройства/компонента
        :rtype: object
        """
        if id_ == 'self':
            return self.device

        return Parser._get_component(id_, self.device.hardware)

    def run_forever(self, routines: List[tuple]) -> NoReturn:
        """Запустить бесконечный цикл исполнения сопрограмм в отдельном потоке.

        Параметры:
          :param routines: — список доступных для исполнения рутин.
        """
        ...

    def apply_config(self, old_data: dict, new_data: dict) -> None:
        """Применить новые настройки конфигурации, заданные пользователем.

        Записать резервную копию текущей конфигурации и новые настройки
        в отдельные файлы.

        :param old_data: текущая конфигурация
        :type old_data: dict
        :param new_data: новые данные для конфигурации
        :type new_data: dict
        """
        self._write_yaml(
            old_data, BACKUP_FILE, default_flow_style=False, sort_keys=False)

        units, complects = {}, {}
        family, id_, pin, params = 0, 1, 2, 3

        for component in new_data.get('units'):
            data = self.set_component_data(component, id_, family, pin, params)

            if component[family].startswith('c'):
                self.update_group(complects, component[family], data)
            else:
                self.update_group(units, component[family], data)

        new_config = {
            'device': new_data.get('device'),
            'snmp': new_data.get('snmp'),
            'mqtt': old_data.get('mqtt'),
            'units': units,
            'complects': complects,
        }
        new_config['snpm']['oids'] = old_data.get('oids')
        print('Новая конфигурация:', new_config)

        self._write_yaml(
            new_config, CONFIG_FILE, default_flow_style=False, sort_keys=False)

    def set_component_data(
            self,
            component: list,
            id_: int,
            family: int,
            pin: int,
            params: int,
    ) -> Dict[str, dict]:
        """Установить данные компоненту для его последующей инициализации.

        :param component: настраиваемый компонент
        :type component: list[str, str, int, dict]
        :param id_: индекс кодового идентификатора компонента
        :type id_: int
        :param family: индекс семейства компонента
        :type family: int
        :param pin: индекс ПИНа компонента
        :type pin: int
        :param params: индекс опциональных параметров компонента
        :type params: int

        :raises ValueError: для правильной настройки необходим словарь

        :return: словарь с данными компонента
        :rtype: dict
        """
        try:
            data = component[params]
            data.pop('alias', None)
        except ValueError:
            msg = 'Для правильной настройки необходим словарь!'
            notify(self.device, msg, no_repr=True, local_only=True)

            raise

        if component[pin] > 0:
            data['pin'] = component[pin]

        return {component[id_]: data}

    @staticmethod
    def update_group(
            group: dict,
            family: str,
            data: dict,
    ) -> None:
        """Обновить словарь группированных компонентов.

        :param group: группа настроенных компонентов
        :type group: dict
        :param family: семейство компонента
        :type family: str
        :param data: данные компонента
        :type data: dict
        """
        if family not in group:
            group[family] = data
        else:
            group[family].update(data)

    def _write_yaml(self, config: dict, file: str, **kwargs) -> None:
        with open(file, 'w') as f:
            yaml.safe_dump(config, f, **kwargs)

    def _set_subscriptions(
            self,
            group: dict = None,
            **kwargs: Callable,
    ) -> None:

        if group is None:
            for subscriber, callback in kwargs.items():
                self.device.reporter.register(subscriber, callback)

            notify(self.device, 'готово.', no_repr=True, local_only=True)

            return

        for family in group.values():
            for component in family.values():
                for subscriber, callback in kwargs.items():
                    component.reporter.register(subscriber, callback)

                notify(component, 'готово.', local_only=True)

    def _blink(self, report: Type[dict]) -> None:
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
        """
        msg_type = report['type']

        if msg_type == 'event':
            self.device.indicators['led2'].blink(1, 1, 1)
        elif msg_type in ('info', 'status'):
            self.device.indicators['led2'].blink(1, 1, 2)
        elif msg_type == 'warning':
            self.device.indicators['led2'].blink(2, 1, 3)
        elif msg_type == 'error':
            self.device.indicators['led2'].blink(3, 1, 3)

    def _publish(self, report: Type[dict]) -> None:
        msg_body = report['message']
        unit = 'self' if report['from'] == self.device.id else report['from']

        if self.is_duplicate(unit, msg_body):
            return

        payload = self._form_payload(report, unit, msg_body)
        pub_data = self._form_pub_data(self.device, report, unit, payload)

        self.device.indicators['led1'].on()
        self.device.client.publish(**pub_data)
        self.sended_messages[unit] = msg_body
        self.device.indicators['led1'].off()

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
            unit: str,
            msg_body: Union[int, str, float],
    ) -> str:
        timestamp = dt.datetime.now().isoformat(sep=' ')
        msg_type = report['type']

        cursor = self.device.db.cursor()
        tables_set = {'events'}
        tabledata = [timestamp, msg_type, unit, str(msg_body)]

        fill_tables(self.device.db, cursor, tables_set, tabledata)

        tables_set.clear()
        tables_set.update({'status', 'status_archive'})
        tabledata.pop(1)

        fill_tables(self.device.db, cursor, tables_set, tabledata)

        return json.dumps((timestamp, msg_type, msg_body))

    @classmethod
    def _form_pub_data(
            cls,
            device: Type[object],
            report: Type[dict],
            unit: str,
            payload: str,
            topic: str = 'report',
    ) -> Dict[str, Union[str, int, bool]]:
        topic = '/'.join([device.id, topic, unit])
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
