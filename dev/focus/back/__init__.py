import json
from datetime import datetime
from time import sleep
from typing import Any, Tuple
from paho.mqtt.client import Client, MQTTMessage

import yaml

from .commands import Handler, Parser
from .feedback import Reporter
from .hardware import Hardware
from .utils import DB_FILE
from .utils.db_tools import get_db, init_db
from .utils.messaging import notify


class FocusPro(Hardware):
    """Класс устройства мониторинга банкоматов, реализующий взаимодействие
    с удалённым сервером по протоколам MQTT v3.1 и SNMP.

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

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # Идентификация:
        self.id = self.config['device']['id']
        self.description = self.config['device']['location']

        msg = 'Настройка внешних зависимостей...'
        notify(self, msg, type_='info', swap=True, local_only=True)

        # Установка репортёра и парсера команд:
        self.reporter = Reporter(self.id)
        self.parser = Parser()

        # Словарь последних отправленных сообщений от имени каждого компонента:
        self.sended_messages = {}

        try:
            # Подключение к локальной базе данных:
            with open(DB_FILE):
                msg = 'Локальная БД уже существует. Инициализация не требуется.'
                notify(self, msg, swap=True, local_only=True)

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
        if rc != 0:
            notify(self, rc, type_='error', swap=True)
        else:
            self.is_connected = True
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

        if rc != 0:
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
        msg = f'Принято сообщение по теме: {message.topic}'
        notify(self, msg, type_='info', swap=True, local_only=True)

        _, topic, *args = message.topic.split('/')
        payload = json.loads(message.payload.decode())

        msg = f'Полезная нагрузка сообщения: {payload}'
        notify(self, msg, type_='info', swap=True, local_only=True)

        if topic == 'cnf':
            self.handler.apply_config(self.config, payload)
            self.handler.execute((1, (self, 'reboot', {})))

        elif topic == 'cmd':
            hardware = self.units, self.complects
            instructions = self.parser.parse_instructions(
                self, payload, hardware)
            self.handler.handle(instructions)

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
