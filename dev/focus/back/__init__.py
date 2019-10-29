"""Основной модуль бэкэнда приложения.

:class FocusPro: класс верхнего уровня, инкапсулирующий логику всего бэкэнда.
"""
import json
from datetime import datetime
from gzip import decompress
from time import sleep
from typing import Any, Iterator, List, Tuple, Union

import yaml
from paho.mqtt.client import Client, MQTTMessage
from pysnmp.hlapi import CommunityData, ContextData, SnmpEngine, UsmUserData

from .commands import Handler, Parser
from .feedback import Reporter
from .hardware import Hardware
from .utils import DB_FILE
from .utils.db_tools import get_db, init_db
from .utils.messaging import notify


class FocusPro(Hardware):
    r"""Класс устройства мониторинга банкоматов, реализующий взаимодействие
    с удалённым сервером по протоколам MQTT v3.1 и SNMP.

    :param **kwargs: опциональный словарь аргументов
    :type **kwargs: dict
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # Идентификация:
        self.id = self.config['device']['name']
        self.description = self.config['device']['address']

        msg = 'настройка внешних зависимостей...'
        notify(self, msg, no_repr=True, local_only=True)

        # Установка репортёра и парсера команд:
        self.reporter = Reporter(self.id)
        self.parser = Parser()

        try:
            # Подключение к локальной базе данных:
            with open(DB_FILE):
                msg = 'инициализация базы данных не требуется.'
                notify(self, msg, no_repr=True, local_only=True)

            self.db = get_db(DB_FILE)
        except OSError:
            # Инициализация новой БД:
            self.db = init_db(self, DB_FILE, self.hardware)

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

        # Конфигурирование SNMP:
        snmp = self.config['snmp']
        snmp['agent'], snmp['port'] = self.parse_snmp_host(snmp)
        snmp['oids'] = snmp.get('oids') or ['1.3.6.1.2.1.1.5.0']
        snmp['credentials'] = self.set_credentials(snmp)
        snmp['engine'] = SnmpEngine()
        snmp['context'] = ContextData()

        # Запуск обработчика событий и команд:
        self.handler = Handler(self)

    def __repr__(self):
        return f'id={self.id}'

    @staticmethod
    def parse_snmp_host(snmp_config: dict) -> Tuple[str, int]:
        """Разбить строку адресных данных хоста на составляющие.

        :param snmp_config: конфигурация SNMP
        :type snmp_config: dict

        :return: адрес и порт для связи с хостом
        :rtype: tuple[str, int]
        """
        host = snmp_config['host'].split(':')

        return host[0], int(host[1])

    @staticmethod
    def set_credentials(snmp_config: dict) -> Union[CommunityData, UsmUserData]:
        """Установить полномочия для аутентификации.

        Тип возвращаемого объекта зависит от используемой версии протокола SNMP.

        :param snmp_config: конфигурация SNMP
        :type snmp_config: dict

        :return: объект с настроенными полномочиями
        :rtype: hlapi.CommunityData or hlapi.UsmUserData
        """
        community = snmp_config['community']

        if int(snmp_config['version'][0]) < 3:
            credentials = CommunityData(community)
        else:
            credentials = UsmUserData(**community)

        return credentials

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

    def connect_async(self, countdown: int = 0) -> None:
        """Подключиться к посреднику асинхронно.

        Если процесс стартует с ошибками связи, следует повысить показатель
        обратного отсчёта до начала соединения.

        :param countdown: время простоя перед подключением, по умолчанию 0
        :type countdown: int
        """
        sleep(countdown)
        broker = self.config['mqtt']['broker']
        self.client.connect_async(**broker)

    def on_connect(
            self,
            client: Client,
            userdata: Any,
            flags: dict,
            rc: int,
    ) -> None:
        """Обработать результат подключения к посреднику.

        :param client: экземпляр объекта клиента MQTT
        :type client: paho.mqtt.client.Client
        :param userdata: пользовательские данные, передаваемые обработчику
        :type userdata: Any
        :param flags: словарь флагов ответа от посредника
        :type flags: dict
        :param rc: код результата подключения
        :type rc: int
        """
        if rc != 0:
            notify(self, rc, report_type='error', no_repr=True)
        else:
            self.client.is_connected = True
            client.unsubscribe(f'{self.id}/#')
            client.subscribe([
                (f'{self.id}/cmd/#', 2),
                (f'{self.id}/cnf/#', 2),
                (f'{self.id}/snmp/#', 2),
            ])
            notify(self, 'online', no_repr=True,
                   report_type='status', retain=True)

    def on_disconnect(
            self,
            client: Client,
            userdata: Any,
            rc: int,
    ) -> None:
        """Обработать результат разъединения с посредником.

        :param client: экземпляр объекта клиента MQTT
        :type client: paho.mqtt.client.Client
        :param userdata: пользовательские данные, передаваемые обработчику
        :type userdata: Any
        :param rc: код результата подключения
        :type rc: int
        """
        self.client.is_connected = False
        notify(self, 'offline', no_repr=True,
               report_type='status', retain=True)

        if rc != 0:
            notify(self, rc, report_type='error', no_repr=True)

    def on_message(
            self,
            client: Client,
            userdata: Any,
            message: MQTTMessage,
    ) -> None:
        """Обработать входящее сообщение.

        Принимаются сообщения двух типов: конфигурация и инструкции.
        Конфигурация применяется после перезагрузки устройства, которая
        инициируется тут же. Инструкции сначала парсятся, а затем передаются
        обработчику на исполнение.

        :param client: экземпляр объекта клиента MQTT
        :type client: paho.mqtt.client.Client
        :param userdata: пользовательские данные, передаваемые обработчику
        :type userdata: Any
        :param message: экземпляр объекта сообщения MQTT
        :type message: paho.mqtt.client.MQTTMessage
        """
        msg = f'сообщение на тему --> {message.topic}'
        notify(self, msg, no_repr=True, local_only=True)

        topic = message.topic.split('/')[1]
        payload = message.payload

        if topic == 'snmp':
            payload = decompress(payload)

        payload = json.loads(payload.decode())

        msg = f'полезная нагрузка --> {payload}'
        notify(self, msg, no_repr=True, local_only=True)

        if topic == 'cmd':
            instructions = self.parser.parse_instructions(
                self, payload, self.hardware)
            self.handler.handle(instructions)

        elif topic == 'cnf':
            self.handler.apply_config(self.config, payload)
            self.handler.execute_command(
                '-2', [(['lock'], 'on', {}), (['self'], 'reboot', {})]
            )

        elif topic == 'snmp':
            pass
            # self.handler.execute_command(
            #     '-3', [(['self'], 'report_at_intervals', payload)]
            # )
