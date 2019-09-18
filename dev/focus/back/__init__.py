import json
import shelve
import subprocess
from datetime import datetime
from time import sleep
from typing import Any, Callable, Dict, Tuple, Union

from paho.mqtt.client import Client, MQTTMessage, MQTTv311, MQTTMessageInfo
import yaml

# from .commands import Handler, Parser
from .feedback import Reporter
from .hardware import Hardware
from .utils import DB_FILE, ROUTINES_FILE
from .utils.db_tools import fill_table, get_db, init_db
from .utils.messaging import notify


class FocusPro(Hardware):
    """Класс устройства мониторинга банкоматов, реализующий взаимодействие
    с удалённым сервером по протоколам MQTT v3.1 и SMNP.

    Методы:
        :meth __init__(self, loop, **kwargs): — инициализировать экземпляр
    класса;
        :meth connect_async(self, countdown=0): — подключиться к посреднику
    асинхронно;
        :meth on_connect(self, client, userdata, flags, rc): — обработать
    результат подключения к посреднику;
        :meth on_disconnect(self, client, userdata, rc): — обработать результат
    разъединения с посредником;
        :meth on_message(self, client, userdata, message): — обработать принятое
    сообщение;
        :meth set_subscriptions(self, *callbacks): — установить внутренних
    подписчиков для регистируемых на устройстве событий.
        :meth blink(self, sender): — осуществлять световую индикацию при
    регистрации событий;
        :meth publish(self, sender) — отправить отчёт посреднику на указанную
    тему.
    """

    def __init__(self) -> None:
        super().__init__()

        msg_body = f'Настройка внешних зависимостей...'
        self.logger.info(msg_body)

        # Идентификация:
        self.id = self.config['device']['id']
        self.description = self.config['device']['location']

        # Регистрация обработчиков событий:
        self.reporter = Reporter(self.id)
        self.set_subscriptions(self.blink, self.publish)

        # Словарь последних отправленных сообщений от имени каждого компонента:
        self.sended_messages = {}

        try:
            # Подключение к хранилищу доступных рутин:
            with shelve.open(ROUTINES_FILE) as db:
                routines = db.items()

                for index, routine in enumerate(routines):
                    print('Routine', index, f'--> {routine}')
        except OSError:
            print('Файл с рутинами отсутствует!')

            raise

        # Установка парсера и обработчика команд:
        # self.parser = Parser()
        # self.handler = Handler(routines)

        try:
            # Подключение к локальной базе данных:
            with open(DB_FILE):
                msg = 'Локальная БД уже существует. Инициализация не требуется.'
                print(msg)

            self.db = get_db(DB_FILE)
        except OSError:
            # Инициализация новой БД:
            self.db = init_db(self, DB_FILE, self.complects, self.units)
        finally:
            # Настройка клиента MQTT:
            self.client = Client(self.id, clean_session=False)
            self.client.is_connected = False
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message

            # Определение последнего завещания:
            LWT = self._define_lwt()
            self.client.will_set(**LWT)

            # Включение внутреннего логирования клиента:
            self.client.enable_logger(self.logger)

    def connect_async(self, countdown: int = 0) -> None:
        """Подключиться к посреднику асинхронно.

        Параметры:
            :param countdown: — время простоя перед подключением (увеличить,
        если процесс стартует с ошибками связи).
        """
        sleep(countdown)
        broker = self.config['mqtt']['broker']
        self.client.connect_async(**broker)
        self.client.loop_start()

    def on_connect(
        self,
        client: Client,
        userdata: Any,
        flags: dict,
        rc: int
    ) -> None:
        """Обработать результат подключения к посреднику.

        Параметры:
            :param client: — экземпляр клиента MQTT;
            :param userdata: — пользовательские данные, передаваемые
        обработчику;
            :param flags: — словарь флагов ответа от посредника;
            :param rc: — код результата подключения.
        """
        if rc:
            notify(self, rc, type_='error', swap=True)
        else:
            self.is_connected = True
            client.unsubscribe(self.id + '/#')
            client.subscribe(
                [
                    (self.id + '/cnf', 2),
                    (self.id + '/cmd', 2),
                ]
            )

            notify(self, 'online', swap=True, type_='status', retain=True)

    def on_disconnect(
        self,
        client: Client,
        userdata: Any,
        rc: int
    ) -> None:
        """Обработать результат разъединения с посредником.

        Параметры:
            :param client: — экземпляр клиента MQTT;
            :paramn userdata: — пользовательские данные, передаваемые
        обработчику;
            :param rc: — код результата подключения.
        """
        self.is_connected = False
        notify(self, 'offline', swap=True, type_='status', retain=True)

        if rc:
            notify(self, rc, type_='error', swap=True)

    def on_message(
        self,
        client: Client,
        userdata: Any,
        message: MQTTMessage
    ) -> None:
        """Обработать принятое сообщение.

        Параметры:
            :param client: — экземпляр клиента MQTT;
            :paramn userdata: — пользовательские данные, передаваемые
        обработчику;
            :param message: — экземпляр MQTTMessage с атрибутами topic, payload,
        qos, retain;
        """
        print('Принято сообщение по теме:', message.topic)

        _, topic, *args = message.topic.split('/')
        payload = json.loads(message.payload.decode())

        print('Полезная нагрузка сообщения:', payload)

        # if topic == 'cnf':
        #     self.handler.apply_config(self.config, payload)
        #     self.handler.run(self, 'reboot')

        # elif topic == 'cmd':
        #     coros = self.parser.parse_instructions(payload)
        #     self.handler.dispatch_routines(coros)

    def is_duplicate(
            self, component: str, msg: Union[int, str, float]) -> bool:
        """Вернуть результат проверки, является ли данное сообщение дубликатом
        последнего отправленного указанным компонентом.

        Параметры:
            :param component: — наименование компонента;
            :param msg: — тело сообщения.
        """
        return msg == self.sended_messages.get(component)

    def set_subscriptions(self, *callbacks: Callable) -> None:
        """Установить внутренних подписчиков для регистрируемых на устройстве
        событий.

        События обрабатываются следующим образом:
        1) подписчик "blink" осуществляет световую индикацию, основанную на
        типе события;
        2) подписчик "pub" отвечает за отправку отчётов посреднику.

        Параметры:
            :param callbacks: — произвольное количество обработчиков событий.
        """
        for family in self.units.values():
            for unit in family.values():
                print('Регистрирую подписчиков для одиночного компонента', unit)

                self.reporter.register(unit, 'blink', callbacks[0])
                self.reporter.register(unit, 'pub', callbacks[1])

        for family in self.complects.values():
            for cmp in family.values():
                print('Регистрирую подписчиков для составного компонента', cmp)

                self.reporter.register(cmp.control, 'blink', callbacks[0])
                self.reporter.register(cmp.control, 'pub', callbacks[1])

        self.reporter.register(self, 'blink', callbacks[0])
        self.reporter.register(self, 'pub', callbacks[1])

    def blink(self, report: Reporter) -> None:
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

        Параметры:
            :param report: — экземпляр репортёра, реализующего интерфейс 
        словаря.
        """
        msg_type = report['type']

        if msg_type == 'event':
            self.indicators['led2'].blink(1, 1, 1)
        elif msg_type in ('info', 'status'):
            self.indicators['led2'].blink(1, 1, 2)
        elif msg_type == 'warning':
            self.indicators['led2'].blink(2, 1, 3)
        elif msg_type == 'error':
            self.indicators['led2'].blink(3, 1, 3)

    def publish(self, report: Reporter) -> None:
        """Отправить отчёт посреднику на указанную тему.

        Рапортирование сопровождается световой индикацией.

        Параметры:
            :param report: — экземпляр репортёра, реализующего интерфейс 
        словаря.
        """
        msg_body = report['message']
        print(msg_body)

        if self.is_duplicate(self.id, msg_body):
            msg_body = f'Сообщение дублирует предыдущее от этого же компонента.'
            self.logger.info(msg_body)

            return

        payload = self._form_payload(report, msg_body)
        pub_data = self._form_pub_data(report, payload)

        self.indicators['led1'].on()
        self.client.publish(**pub_data)
        self.sended_messages[self.id] = msg_body
        self.indicators['led1'].off()

    def _form_payload(
        self,
        report: Reporter,
        msg_body: Union[int, str, float]
    ) -> str:
        timestamp = datetime.now().isoformat(sep=' ')
        msg_type = report['type']
        unit = 'self' if report['from'] == self.id else report['from']

        cursor = self.db.cursor()
        tables_set = {'events'}
        tabledata = [timestamp, msg_type, unit, str(msg_body)]

        fill_table(self.db, cursor, tables_set, tabledata)

        tables_set.clear()
        tables_set.update({'status', 'status_archive'})
        tabledata.pop(1)

        fill_table(self.db, cursor, tables_set, tabledata)

        return json.dumps((timestamp, msg_type, msg_body))

    def _form_pub_data(
        self,
        report: Reporter,
        payload: str
    ) -> Dict[str, Union[str, int, bool]]:
        topic = '/'.join([self.id, 'report', report['from']])
        qos = report['qos']
        retain = report['retain']

        return {
            'topic': topic,
            'payload': payload,
            'qos': qos,
            'retain': retain,
        }

    def _define_lwt(self, qos: int = 2, retain: bool = True):
        timestamp = datetime.now().isoformat(sep=' ')
        msg_type = 'status'
        msg_body = 'offline'

        topic = '/'.join([self.id, 'report', 'self'])
        payload = timestamp, msg_type, msg_body

        return {
            'topic': topic,
            'payload': json.dumps(payload),
            'qos': qos,
            'retain': retain,
        }

    def _define_broker(self, broker: dict) -> Tuple[str, int, int]:
        return broker['host'], broker['port'], broker['keepalive']
