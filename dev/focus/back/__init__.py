import json
import shelve
import subprocess
from datetime import datetime
from time import sleep
from typing import Any

import paho.mqtt.client as mqtt
import yaml

from .feedback.Reporter import Reporter
from .hardware import Hardware
from .utils import BACKUP_FILE, CONFIG_FILE, DB_FILE
from .utils.concurrency import run_async
from .utils.db_handlers import fill_table, get_db, init_db
from .utils.messaging_tools import notify, register
from .utils.routines.Handler import Handler
# from .utils.routines.Parser import Parser


class FocusPro(Hardware):
    """Обвязка функционала MQTT вокруг :class Hardware: без учета авторизации."""

    def __init__(self, **kwargs):
        super().__init__()

        msg_body = f'Настройка внешних зависимостей...'
        self.logger.info(msg_body)

        # Идентификация:
        self.id = self.config['device']['id']
        self.description = self.config['device']['location']

        # Регистрация обработчиков событий:
        self.reporter = Reporter(self.id)
        self.set_subscriptions(self.blink, self.publish)

        # Установка обработчиков поступающих команд:
        self.handler = Handler()

        try:
            # Подключение к локальной базе данных:
            with open(DB_FILE):
                msg = 'Локальная БД уже существует. Инициализация не требуется.'
                print(msg)

            self.db = get_db(DB_FILE)
        except IOError:
            # Инициализация новой БД:
            self.db = init_db(DB_FILE, self.complects, self.units)
        finally:
            # Настройка клиента MQTT:
            self.client = mqtt.Client(self.id, False)
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message

            # Определение последнего завещания:
            LWT = self.define_lwt()
            self.client.will_set(**LWT)

            # Включение внутреннего логирования клиента:
            self.client.enable_logger(self.logger)

        # Установка значений по умолчанию:
        self.is_connected = False
        self.recent_messages = set()

    def connect(self, timeout=0) -> None:
        """Подключиться к посреднику асинхронно."""

        sleep(timeout)
        device = self.config.get('device')
        broker = self._define_broker(device['broker'])
        self.client.connect_async(*broker)
        self.client.loop_start()

    def on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: dict,
        rc: int
    ) -> None:
        if rc:
            notify(self, rc, type_='error', swap=True)
        else:
            self.is_connected = True

            notify(
                self, 'online', swap=True, type_='status', retain=True
            )

            client.subscribe(
                [
                    (self.id + '/#', 2),
                ]
            )

    def on_disconnect(self, client, userdata, rc):
        self.is_connected = False
        notify(self, 'offline', swap=True, type_='status', retain=True)

        if rc:
            notify(self, rc, type_='error', swap=True)

    def on_message(self, client, userdata, message):
        print('Принято сообщение по теме:', message.topic)

        _, topic, *routine = message.topic.split('/')
        payload = json.loads(message.payload.decode())

        print('Полезная нагрузка сообщения:', payload)

        if topic == 'cnf':
            self.apply_config(payload)

        elif topic == 'cmd':
            # Parser.parse_instructions(self.conn, payload)
            pass


#        print(message.topic, str(message.payload), sep='\n')

  #      command = message.topic.split('/')[-1]
   #     payload = json.loads(message.payload)
    #    changed_unit = payload[0]
     #   target_unit = payload[1]
      #  time_limit = payload[2]

       # on_event(command, changed_unit, target_unit, time_limit=time_limit)

    def set_subscriptions(self, *callbacks):
        """Зарегистрировать устройство и его компоненты для рапортирования.

        События обрабатываются следующим образом:
        1) подсписчик "blink" осуществляет световую индикацию, основанную на
        типе события;
        2) подписчик "pub" отвечает за отправку отчётов посреднику.
        """

        for family in self.units.values():
            for unit in family.values():
                print('Регистрирую подписчиков для одиночного компонента', unit)

                register(unit, 'blink', callbacks[0])
                register(unit, 'pub', callbacks[1])

        for family in self.complects.values():
            for cmp in family.values():
                print('Регистрирую подписчиков для составного компонента', cmp)

                register(cmp.control, 'blink', callbacks[0])
                register(cmp.control, 'pub', callbacks[1])

        register(self, 'blink', callbacks[0])
        register(self, 'pub', callbacks[1])

    # def apply_workers(self, services):
    #     self.workers = set()

    #     for service in services:
    #         self.workers.add(Async(service))

    def blink(self, sender: dict):
        """Моргать при регистрации событий.

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
          :param sender: — объект компонента, осуществляющего отправку отчётов
        от своего имени через реализацию словаря с данными.
        """

        msg_type = sender[sender.topic]['type']

        if msg_type == 'event':
            self.indicators['led2'].blink(1, 1, 1)
        elif msg_type in ('info', 'status'):
            self.indicators['led2'].blink(1, 1, 2)
        elif msg_type == 'warning':
            self.indicators['led2'].blink(2, 1, 3)
        elif msg_type == 'error':
            self.indicators['led2'].blink(3, 1, 3)

    def publish(self, sender: dict):
        """Отправка отчёта посреднику по указанной теме.

        Рапортирование сопровождается световой индикацией.

        Параметры:
          :param sender: — объект отчёта, содержащий необходимые данные
        для формирования структуры результирующего сообщения.
        """

        report = sender[sender.topic]
        payload = self._form_payload(report)

        if isinstance(payload, ()):
            msg_body = f'Сообщение было продублировано: {payload}'
            self.logger.info(msg_body)

            return

        pub_data = self._form_pub_data(sender.topic, report, payload)

        self.indicators['led1'].on()
        self.client.publish(**pub_data)
        self.indicators['led1'].off()

    def _form_payload(self, report: dict):
        """Сформировать JSON-строку с данными для отправки посреднику.

        Записать данные в локальную БД, а затем вернуть строку JSON,
        преобразованную из кортежа со значениями, необходимыми для операций с
        БД на хосте посредника.

        Параметры:
          :param report: — словарь содержимого для отчёта.
        """

        msg_body = report['message']

        if report['from'] == self.id:
            report['from'] = 'self'

        payload = report['from'], msg_body
        print('Полезная нагрузка до проверки:', payload)

        if self.is_duplicate(payload):
            return payload

        timestamp = datetime.now().isoformat(sep=' ')
        msg_type = report['type']
        tabledata = [timestamp, msg_type, *payload]

        cursor = self.db.cursor()
        tables_set = {'events'}

        fill_table(self.db, cursor, tables_set, tabledata)

        tabledata.pop(1)

        tables_set.clear()
        tables_set.update({'status', 'status_archive'})

        fill_table(self.db, cursor, tables_set, tabledata)

        payload = timestamp, msg_type, msg_body

        return json.dumps(payload)

    def _form_pub_data(self, topic: str, report: dict, payload: str):
        """Сформировать объект с данными для публикации отчёта.

        Параметры:
          :param topic: — тема сообщения;
          :param report: — словарь отчёта, содержащий необходимые данные
        для подготовки сообщения к отправке;
          :param payload: — строка с отправляемыми данными в формате JSON.

        Вернуть объект словаря для связывания с методом publish() клиента MQTT.
        """

        topic = '/'.join([self.id, topic, report['from']])
        qos = report['qos']
        retain = report['retain']

        return {
            'topic': topic,
            'payload': payload,
            'qos': qos,
            'retain': retain,
        }

    def define_lwt(self, qos=2, retain=True):
        """Определить завещание для отправки посреднику
        в случае непредвиденного разрыва связи.
        """

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

    def _define_broker(self, broker: dict):
        """Определить адрес хоста и порт, через который будет осуществляться
        обмен данными с посредником, а также допустимое время простоя между
        отправкой сообщений в секундах.

        Параметры:
        :param broker: — словарь с данными о посреднике.

        Вернуть кортеж вида: (адрес, порт, время простоя).
        """

        return broker['host'], broker['port'], broker['keepalive']

    def is_duplicate(self, data: list):
        """Определить, является ли подготовленное сообщение дубликатом
        предыдущего по данной теме.

        Параметры:
        :param data: — список из элементов, формирующих структуру сообщения.
        """

        return data in self.recent_messages

    def apply_config(self, config_data):
        """Применить новые настройки конфигурации, заданные пользователем.

        Для вступления изменений в силу, устройство перезагружается сразу после
        записи новых настроек в файл БД.

        Параметры:
          :param config_data: — объект словаря с новой конфигурацией.
        """

        family, unit, pin, params = 0, 1, 2, 3
        id_, location = config_data.pop(-1)
        new_config = {
            'device': {
                'id': id_,
                'location': location,
                'broker': self.config['device']['broker'],
            },
            'units': {},
        }

        for i in config_data:
            print('Item:', i)

            if i[family] not in new_config['units']:
                new_config['units'].update({i[family]: {}})

            if i[pin] > 0:
                new_config['units'][i[family]][i[unit]] = {
                    'pin': i[pin],
                }
            elif i[params]:
                new_config['units'][i[family]][i[unit]] = i[params]
            else:
                new_config['units'][i[family]][i[unit]] = {}

        new_config.update({'complects': {'couts': {}}})

        couts = new_config['units'].pop('couts')
        new_config['complects']['couts'].update(
            {
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
        )

        # cf = open(CF)

        # with open(BACKUP_FILE, 'w') as bf:
        #     bf.writelines(cf.readlines())

        # cf.close()

        with shelve.open(CONFIG_FILE) as db:
            for category, contents in new_config.items():
                db[category] = contents
            # yaml.dump(new_config, cf, default_flow_style=False)

        # self.client.loop_stop()
        # self.client.disconnect()
        # subprocess.run('/usr/bin/sudo reboot', shell=True)
