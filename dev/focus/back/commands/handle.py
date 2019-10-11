import asyncio
import datetime as dt
import gzip
import json
import operator
import shelve
import subprocess
# from concurrent.futures import ThreadPoolExecutor
# from functools import partial
from time import sleep
from typing import (
    Any, Callable, Dict, Iterator, List, NoReturn, Tuple, Type, Union
)

import yaml
from pysnmp import hlapi

from ..utils import BACKUP_FILE, COMMANDS_FILE, CONFIG_FILE
from ..utils.db_tools import fill_tables
from ..utils.messaging import notify
from .parse import Parser

ShelveDB = shelve.DbfilenameShelf


class CommandsRegistry:

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
        :type device: object
        :param target: IP или адрес удалённого устройства
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
        :param start_from: номер узла, с которого необходимо начать выборку,
        по умолчанию None
        :type start_from: int or None
        """
        engine = engine or device.config['snmp']['engine']
        context = context or device.config['snmp']['context']
        args = target, oids, credentials, engine, context, port

        if start_from is not None:
            print('CHECK')
            if isinstance(count, int) and count > 1:
                print('get bulk')
                snmp_data = cls.snmp_get_bulk(*args, count, start_from)
            else:
                print('get bulk auto')
                snmp_data = cls.snmp_get_bulk_auto(*args, count, start_from)
        else:
            snmp_data = cls.snmp_get_data(*args)

        snmp_data = json.dumps(snmp_data)
        gzip_bytes = gzip.compress(snmp_data.encode())

        mqtt_settings = {'qos': 1, 'retain': False}
        pub_data = device.handler._form_pub_data(
            mqtt_settings, device, gzip_bytes, unit='all', topic='snmp')

        device.indicators['led1'].on()
        device.client.publish(**pub_data)
        device.indicators['led1'].off()

    @classmethod
    def snmp_get_data(
            cls,
            target: str,
            oids: List[str],
            credentials: Union[hlapi.CommunityData, hlapi.UsmUserData],
            engine: hlapi.SnmpEngine,
            context: hlapi.ContextData,
            port: int,
    ) -> str:
        """Получить значение отдельного объекта в базе управляющей информации.

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

        return cls.fetch(snmp_handler, 1)[0]

    @classmethod
    def snmp_get_bulk(
            cls,
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
        :param count: количество экземпляров объекта
        :type count: int
        :param start_from: номер узла, с которого необходимо начать выборку,
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

        return cls.fetch(snmp_handler, count)

    @classmethod
    def snmp_get_bulk_auto(
            cls,
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
        count = cls.snmp_get_data(
            target, [count_oid], credentials, engine, context, port
        )[count_oid]
        print('COUNT:', count)

        return cls.snmp_get_bulk(
            target, oids, credentials, engine, context, port, count, start_from)

    @staticmethod
    def construct_object_types(list_of_oids: List[str]) -> List[str]:
        """Сконструировать специальные объекты для выборки данных.

        :param list_of_oids: идентификаторы объектов
        :type list_of_oids: list[str]

        :return: объекты для передачи в функцию выборки
        :rtype: list[str]
        """
        return [
            hlapi.ObjectType(hlapi.ObjectIdentity(oid)) for oid in list_of_oids
        ]

    @classmethod
    def fetch(cls, snmp_handler: Iterator, count: int) -> List[dict]:
        """Выбрать данные, возвращаемые обработчиком GET запросов.

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
                    notify(
                        Handler.device, msg, no_repr=True, report_type='error')

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
    def reboot(cls, device: list) -> NoReturn:
        """Перезагрузить устройство.

        Перезагрузка с интервалом меньше, чем в минуту, не позволяется.

        :param device: экземпляр объекта устройства
        :type device: list
        """
        device = device[0]

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

        return timediff < dt.timedelta(seconds=60)

    @staticmethod
    def on(components: list, **kwargs) -> None:
        r"""Включить пин компонента.

        :param component: экземпляр объекта компонента
        :type component: object
        :param **kwargs: опциональные именованные аргументы
        :type **kwargs: dict
        """
        for component in components:
            component.on(**kwargs)

    @staticmethod
    def off(components: list, **kwargs) -> None:
        r"""Выключить пин компонента.

        :param component: экземпляр объекта компонента
        :type component: object
        :param **kwargs: опциональные именованные аргументы
        :type **kwargs: dict
        """
        for component in components:
            component.off(**kwargs)

    @staticmethod
    def toggle(components: list, **kwargs) -> None:
        r"""Изменить состояние пина компонента на противоположное.

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
        self.focus = device
        self.routines = self._get_routines()

        for i, (k, v) in enumerate(self.routines.items(), start=1):
            print(f'Рутина {i}) {k}: {v}')

        # Словарь последних отправленных сообщений от имени каждого компонента:
        self.sended_messages = {}

        # Регистрация обработчиков событий:
        msg = 'регистрирую подписчиков...'
        notify(device, msg, no_repr=True, local_only=True)

        for group in (self.focus.hardware).values():
            self._set_subscriptions(
                self.focus, group, blink=self._blink, pub=self._publish)

        self._set_subscriptions(
            self.focus, blink=self._blink, pub=self._publish)

    @property
    def device(self):
        return self.focus

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

    def execute_command(
            self,
            command_id: str,
            actions: list
    ) -> None:
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

    def perform_action(self, components: list, action: str, kwargs: dict) -> Any:
        """Выполнить действие.

        :param components: цель совершаемого действия
        :type components: list
        :param action: название функции обработки указанного действия
        :type action: str
        :param kwargs: передаваемые обработчику именованные аргументы
        :type kwargs: dict

        :return: результат выполненного действия
        :rtype: Any
        """
        cmd = getattr(CommandsRegistry, action)
        print('performing action...')

        for i, c in enumerate(components):
            c = self.device if c == 'self' else Parser._get_component(
                c, self.device.hardware)
            print(f'target {i}:', c)
            components[i] = c

        print('components:', components)
        print('kwargs:', kwargs)

        return cmd(components, **kwargs)

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

        for component in new_data.get('units'):
            data = self.set_component_data(component, id_, family, pin, params)

            if component[family].startswith('c'):
                self.update_group(complects, component, data, id_, family)
            else:
                self.update_group(units, component, data, id_, family)

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

        Если компоненту назначен псевдоним, использовать его в качестве
        идентификатора вместо установленного по умолчанию.

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
            alias = data.pop("alias")
        except ValueError:
            msg = 'Для правильной настройки необходим словарь!'
            notify(self.device, msg, no_repr=True, local_only=True)

            raise
        except KeyError:
            pass
        else:
            component[id_] = alias

        if component[pin] > 0:
            data['pin'] = component[pin]

        return {component[id_]: data}

    @staticmethod
    def update_group(
            group: dict,
            component: list,
            data: dict,
            id_: int,
            family: int,
    ) -> None:
        """Обновить словарь группированных компонентов.

        :param group: группа настроенных компонентов
        :type group: dict
        :param component: добавляемый компонент
        :type component: list
        :param data: данные компонента
        :type data: dict
        :param id_: индекс кодового идентификатора компонента
        :type id_: int
        :param family: индекс семейства компонента
        :type family: int
        """
        if component[family] not in group:
            group[component[family]] = data
        else:
            group[component[family]].update(data)

    def _write_yaml(self, config: dict, file: str, **kwargs) -> None:
        with open(file, 'w') as f:
            yaml.safe_dump(config, f, **kwargs)

    @staticmethod
    def _set_subscriptions(
            device: Type[object],
            group: dict = None,
            **kwargs: Callable,
    ) -> None:
        if group is None:
            for subscriber, callback in kwargs.items():
                device.reporter.register(subscriber, callback, device)

            notify(device, 'готово.', no_repr=True, local_only=True)

            return

        for family in group.values():
            for component in family.values():
                for subscriber, callback in kwargs.items():
                    component.reporter.register(subscriber, callback, device)

                notify(component, 'готово.', local_only=True)

    @staticmethod
    def _blink(report: Type[dict], device: Type[object]) -> None:
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
        pub_data = self._form_pub_data(report, device, payload, unit)

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

    @staticmethod
    def _form_payload(
        report: Type[dict],
        device: Type[object],
        unit: str,
        msg_body: Union[int, str, float],
    ) -> str:
        timestamp = dt.datetime.now().isoformat(sep=' ')
        msg_type = report['type']

        cursor = device.db.cursor()
        tables_set = {'events'}
        tabledata = [timestamp, msg_type, unit, str(msg_body)]

        fill_tables(device.db, cursor, tables_set, tabledata)

        tables_set.clear()
        tables_set.update({'status', 'status_archive'})
        tabledata.pop(1)

        fill_tables(device.db, cursor, tables_set, tabledata)

        return json.dumps((timestamp, msg_type, msg_body))

    @staticmethod
    def _form_pub_data(
        report: Type[dict],
        device: Type[object],
        payload: str,
        unit: str,
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
