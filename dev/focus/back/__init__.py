import json
from time import sleep
from datetime import datetime
from threading import Thread

import paho.mqtt.client as mqtt

from .hardware import Hardware
from .reporting import Reporter
from .utils import DB_FILE
from .utils.concurrency import Worker
from .utils.db_handlers import fill_table
from .utils.messaging_tools import register, log_and_report


class Connector(Hardware):
    """Обвязка функционала MQTT вокруг :class Hardware: без учета авторизации."""

    def __init__(self, **kwargs):
        super().__init__()

        self.description = self.config['device']['description']

        self.reporter = Reporter(self.id)
        self.register_device(self._blink, self.report_on_topic)

        msg_body = 'запуск %s' % self.id
        log_and_report(self, msg_body, msg_type='info')

        self.is_connected = False
        self.define_broker(**self.config['device']['broker'])

        self.client = mqtt.Client(self.id, False)
        self.client.on_connect = self.on_connect
        # self.client.on_message = self.on_message
        LWT = self._set_status_message('оффлайн', qos=0)
        self.client.will_set(**LWT)
        self.establish_connection(3)

        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc:
            msg_body = 'проблемы с соединением, код %s' % rc
            log_and_report(self, msg_body, msg_type='error')
        else:
            self.is_connected = True
            self.report_on_topic('онлайн')

            # Подписка на акции.
            self.client.subscribe(self.id + '/action/#', qos=1)

    def on_disconnect(self, client, userdata, rc):
        self.is_connected = False

        if rc == 0:
            self.report_on_topic('оффлайн')
        else:
            msg_body = 'соединение прервано, код %s' % rc
            log_and_report(self, msg_body, msg_type='error')

    # def on_message(self, client, userdata, message):
    #     msg_body = 'Инструкция %s [%s]' % (
    #         message.topic, str(message.payload))
    #     self.logger.info(msg_body)

    #     # Десериализация JSON запроса.
    #     data = json.loads(message.payload)

    #     if data['method'] == 'getFocuspioStatus':
    #         # Вернуть статус FocusPIO.
    #         pass
    #     elif data['method'] == 'setFocuspioStatus':
    #         # Обновить статус FocusPIO и отправить ответ.
    #         pass

    def register_device(self, *callbacks):
        """Зарегистрировать устройство и его компоненты для рапортирования.

        Отправка отчётов осуществляется по трём каналам:
        1) каждое событие регистрируется подсписчиком "blink", который
        осуществляет световую индикацию, основанную на типе события;
        2) события, связанные с взаимодействием устройства и посредника,
        записываются на имя "client" от имени самого устройства;
        3) все компоненты разделяются на группы по функциональности, на имя
        которых и направляются отчёты о состоянии этих компонентов.
        """

        self._register_self(*callbacks)
        self._register_units(*callbacks)

    def _register_self(self, *callbacks):
        """Зарегистрировать само устройство для рапортирования.

        Параметры:
            :param callbacks: — кортеж из функций-обработчиков, которые будут
        привязаны к экземпляру устройства.
        """

        register(self, 'blink', callbacks[0])
        register(self, 'client', callbacks[1])

    def _register_units(self, *callbacks):
        """Зарегистрировать все компоненты устройства для рапортирования.

        Параметры:
            :param callbacks: — кортеж из функций-обработчиков, которые будут
        привязаны к каждому компоненту устройства.
        """

        for group_name, grouped_components in self.units.items():
            for unit in grouped_components:
                register(grouped_components[unit],
                         'blink', callbacks[0])
                register(grouped_components[unit], group_name, callbacks[1])

    def define_broker(self, **kwargs):
        """Установить параметры посредника."""

        self.broker = kwargs.pop('host', '89.223.27.69')
        self.port = kwargs.pop('port', 1883)
        self.keepalive = kwargs.pop('keepalive', 60)

    def establish_connection(self, sec_to_wait: int):
        """Установить содинение с посредником.

        Делать попытки подключения до тех пор, пока связь не будет налажена.

        Параметры:
            :param sec_to_wait: — время в секундах, определяющее интервал
        между попытками подключения к посреднику.
        """

        error_reported = False

        while not self.is_connected:
            try:
                self.client.connect(
                    self.broker,
                    self.port,
                    self.keepalive)
            except:
                if not error_reported:
                    msg_body = 'не удаётся установить связь с посредником'
                    log_and_report(self, msg_body, msg_type='error')
                    error_reported = True

                sleep(sec_to_wait)

    def _blink(self, msg):
        """Моргать при регистрации событий.

        Индикация производится следующим образом:
        1) event — светодиод включается на секунду, затем выключается, единожды;
        2) info — светодиод включается на секунду, отключается на одну, дважды;
        3) warning — светодиод включается на две секунды, отключается на одну,
        трижды;
        4) error — светодиод включается на одну секунду, выключается на одну,
        десять раз кряду.

        Параметры:
            :dict msg: — объект компонента, осуществляющего отправку отчётов
        от своего имени через реализацию словаря с данными.
        """

        msg_type = msg['report']['msg_type']

        if msg_type == 'event':
            self.indicators['led2'].blink(1, 1, 1)
        elif msg_type == 'info':
            self.indicators['led2'].blink(1, 1, 2)
        elif msg_type == 'warning':
            self.indicators['led2'].blink(2, 1, 3)
        elif msg_type == 'error':
            self.indicators['led2'].blink(1, 1, 10)

    def report_on_topic(self, report):
        """Отправка отчёта посреднику по указанной теме.

        Рапортирование сопровождается световой индикацией.

        Параметры:
            :param report: — содержание отчёта в виде словаря.
        Если определён ключ 'status', формируется отчёт о текущем состоянии
        устройства/компонента.
        В противном случае, оформляется отчёт о произошедшем событии.
        """

        timestamp = datetime.now().isoformat(sep=' ')
        inscribed = self._form_report(report)
        msg_type = inscribed.pop('type')
        msg_body = inscribed['payload']

        if msg_type == 'status' and msg_body not in ('онлайн', 'оффлайн'):
            tabledata = [timestamp, report.pin, inscribed['to'],
                         inscribed['from'], report.description, msg_body]
        else:
            report = self._set_event_report(msg)

            tabledata = [timestamp, msg_type, msg['to'],
                         msg['from'], msg['report']['msg_body']]
            fill_table(self.conn, 'events', tabledata)

        self.indicators['led1'].on()
        self.client.publish(**report)
        self.indicators['led1'].off()

    def _set_status_report(self, msg):
        """Сформировать отчёт о текущем состоянии устройства/компонента.

        Параметры:
            :param msg: — тело сообщения;
            :param qos: — уровень доставки от 0 до 2;

        Вернуть словарь для метода publish() клиента MQTT.
        """

        if msg['report']['msg_body'] not in ('онлайн', 'оффлайн'):
            timestamp = datetime.now()
            pin, family, id, description, state = msg['pin'], msg['family'],
            msg['id'], msg['description'], msg['state']
            tabledata = [timestamp, **msg]
            fill_table(self.conn, 'gpio_status', tabledata)
            fill_table(self.conn, 'gpio_status_archive', tabledata)

            topic += '/gpio/%s/%s' % (msg[2], msg[3])
            payload = tabledata.insert(1, self.id)

        return {
            'topic': topic,
            'payload': payload,
            'qos': qos,
            'retain': retain,
        }

    def _form_report(self, msg):
        """Сформировать отчёт.

        Параметры:
            :param msg: — словарь, содержащий необходимые данные сообщения;
            :param qos: — уровень доставки от 0 до 2;

        Вернуть словарь для метода publish() клиента MQTT с дополнительным
        ключом 'type', необходимым для определения, какие именно данные будут
        переданы в качестве полезной нагрузки.
        """

        msg_type = msg['report']['msg_type']

        topic = '%s/%s/%s/%s/%s' % (
            self.id,
            'report',
            msg['to'],
            msg['from'],
            msg_type,
        )
        payload = msg['report']['msg_body']
        qos = msg['report']['qos']
        retain = msg['report']['retain']

        return {
            'type': msg_type,
            'topic': topic,
            'payload': payload,
            'qos': qos,
            'retain': retain,
        }
