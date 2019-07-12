import json
from time import sleep
from datetime import datetime

import paho.mqtt.client as mqtt

from .hardware import Hardware
from .reporting import Reporter
from .utils import DB_FILE
from .utils.db_handlers import init_db, get_device_id, define_broker, fill_table
from .utils.messaging_tools import register, log_and_report


class FocusPro(Hardware):
    """Обвязка функционала MQTT вокруг :class Hardware: без учета авторизации."""

    def __init__(self, **kwargs):
        super().__init__()

        self.pin = None
        self.description = self.config['device']['location']

        self.conn = init_db(DB_FILE, self.config, self.units)
        self.id = get_device_id(self.conn)

        self.reporter = Reporter(self.id)
        self.make_subscriptions(self.blink, self.publish)

        self.client = mqtt.Client(self.id, False)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        LWT = self.define_lwt()
        self.client.will_set(**LWT)

        msg_body = 'starting %s' % self.id
        log_and_report(self, msg_body, type_='info', swap=True)

        self.is_connected = False
        self.client.connect(*define_broker(self.conn))
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc:
            log_and_report(self, rc, type_='error', swap=True)
        else:
            self.is_connected = True
            log_and_report(
                self, 'online', type_='status', swap=True, retain=True
            )

            # Подписка на акции.
            client.subscribe(self.id + '/action/#', qos=2)

    def on_disconnect(self, client, userdata, rc):
        self.is_connected = False
        log_and_report(self, 'offline', type_='status', swap=True, retain=True)

        if rc:
            log_and_report(self, rc, type_='error', swap=True)

    def on_message(self, client, userdata, message):
        print(message.topic, str(message.payload), sep='\n')

    # #     msg_body = 'Инструкция %s [%s]' % (
    # #         message.topic, str(message.payload))
    # #     self.logger.info(msg_body)

    # #     # Десериализация JSON запроса.
    # #     data = json.loads(message.payload)

    # #     if data['method'] == 'getFocuspioStatus':
    # #         # Вернуть статус FocusPIO.
    # #         pass
    # #     elif data['method'] == 'setFocuspioStatus':
    # #         # Обновить статус FocusPIO и отправить ответ.
    # #         pass

    def make_subscriptions(self, *callbacks):
        """Зарегистрировать устройство и его компоненты для рапортирования.

        События обрабатываются следующим образом:
        1) подсписчик "blink" осуществляет световую индикацию, основанную на
        типе события;
        2) подписчик "pub" отвечает за отправку отчётов посреднику.
        """

        register(self, 'blink', callbacks[0])
        register(self, 'pub', callbacks[1])

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

        msg_type = report['type']
        msg_body = report['message']

        if report['from'] == self.id:
            report['from'] = 'self'

        timestamp = datetime.now().isoformat(sep=' ')
        tabledata = [timestamp, msg_type, report['from'], msg_body]

        cursor = self.conn.cursor()
        tables_set = {'events'}

        fill_table(self.conn, cursor, tables_set, tabledata)

        tabledata.pop(1)

        tables_set.clear()
        tables_set.update({'status', 'status_archive'})

        fill_table(self.conn, cursor, tables_set, tabledata)

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

    def define_lwt(self):
        """Определить завещание для отправки посреднику
        в случае непредвиденного разрыва связи.
        """

        timestamp = datetime.now().isoformat(sep=' ')
        msg_type = 'status'
        msg_body = 'offline'

        topic = '/'.join([self.id, 'report', 'self'])
        payload = timestamp, msg_type, msg_body
        qos = 1
        retain = True

        return {
            'topic': topic,
            'payload': json.dumps(payload),
            'qos': qos,
            'retain': retain,
        }
