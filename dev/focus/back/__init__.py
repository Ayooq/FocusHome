import json
from time import sleep
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

        self.set_broker(**self.config['device']['broker'])

        self.client_id = kwargs.pop('id', str(self.ident))
        self.client = mqtt.Client(self.client_id, False)

        # Регистрация функций обработки.
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.reporter = Reporter(self.ident)

        self.register_units(self._blink, self._report_on_topic)
        # Зарегистрировать само устройство для рапортирования о своём текущем статусе.
        # register(self, 'alive', self.report_on_topic)

        # self.service = Worker(self.connection_maintenance)
        # Worker(self.ping)

        log_and_report(self, 'Запуск %s' % self.ident, msg_type='info')

        while not self.is_connected:
            try:
                self.client.connect(
                    self.broker,
                    self.port,
                    self.keepalive)
            except:
                msg_body = 'Проблемы с настройкой подключения к посреднику!'
                log_and_report(self, msg_body, msg_type='error')

                sleep(3)

    @property
    def ident(self):
        return self.config['device']['id']

    def set_broker(self, **kwargs):
        """Установить параметры посредника."""

        self.broker = kwargs.pop('host', '89.223.27.69')
        self.port = kwargs.pop('port', 1883)
        self.keepalive = kwargs.pop('keepalive', 60)
        self.is_connected = False

    def on_connect(self, client, userdata, flags, rc):
        """Обработка подключения.

        Кодовые обозначения для :param rc: результирующего кода:
            0: соединение установлено;
            1: в соединении отказано -- некорректная версия протокола;
            2: в соединении отказано -- неправильный идентификатор клиента;
            3: в соединении отказано -- сервер недоступен;
            4: в соединении отказано -- неверные имя пользователя/пароль;
            5: в соединении отказано -- авторизация не прошла;
            6-255: в данный момент не используются;
        """
        if rc:
            msg_body = 'В соединении с %s отказано! Код ответа: [%s]' % (
                self.broker, rc
            )
            log_and_report(
                self,
                msg_body,
                msg_type='error'
            )
        else:
            self.is_connected = True
            msg_body = 'Соединение с %s установлено.' % self.broker
            log_and_report(self, msg_body, msg_type='info')

            # Подписка на акции.
            self.client.subscribe(self.ident + '/action/#', qos=2)

            # Вывести соединение в отдельный поток и слушать события.
            self.client.loop_start()

    def on_disconnect(self, client, userdata, rc):
        self.is_connected = False
        msg_body = 'Остановка работы %s' % self.ident
        log_and_report(self, msg_body, msg_type='info')

        if not rc:
            self.client.loop_stop()

    # def on_publish(self, client, userdata, mid):
    #     fill_table(self.conn, 'events', msg.payload)

    def on_message(self, client, userdata, msg):
        msg_body = 'Инструкция %s [%s]' % (
            msg.topic, str(msg.payload))
        log_and_report(self, msg_body, msg_type='info')

        # Десериализация JSON запроса.
        data = json.loads(msg.payload)

        if data['method'] == 'getFocuspioStatus':
            # Вернуть статус FocusPIO.
            client.publish(
                msg.topic.replace('request', 'response'),
                #   get_gpio_status(), qos=2
            )
        elif data['method'] == 'setFocuspioStatus':
            # Обновить статус FocusPIO и отправить ответ.
            client.publish(
                msg.topic.replace('request', 'response'),
                #   get_gpio_status(), qos=2
            )
        #   client.publish(, get_gpio_status(), 1)

    def register_units(self, *callbacks):
        """Зарегистрировать все компоненты устройства для рапортирования.

        Отправка отчётов осуществляется по двум каналам:
        1) каждое событие регистрируется подсписчиком "blink", который
        осуществляет световую индикацию во время обмена информацией с
        посредником;
        2) все компоненты разделяются на группы по функциональности, на имя
        которых и направляются отчёты о состоянии этих компонентов.

        Параметры:
            :tuple callbacks: — кортеж из функций-обработчиков, которые будут
        привязаны к каждому компоненту устройства.
        """

        for group_name, grouped_components in self.units.items():
            for unit in grouped_components:
                register(grouped_components[unit],
                         'blink', callbacks[0])
                register(grouped_components[unit], group_name, callbacks[1])

    def _blink(self, report):
        """Моргать при регистрации определённых событий.

        Индикация производится следующим образом:
        1) event — светодиод включается на секунду, затем выключается, единожды;
        2) info — светодиод включается на секунду, отключается на одну, дважды;
        3) warning — светодиод включается на две секунды, отключается на одну,
        трижды;
        4) error — светодиод включается на одну секунду, выключается на одну,
        десять раз кряду.

        Параметры:
            :dict report: — объект компонента, осуществляющего отправку отчётов
        от своего имени через реализацию словаря с данными.
        """

        msg_type = report['report']['type']

        if msg_type == 'event':
            self.units['leds']['led2'].blink(1, 1, 1)
        elif msg_type == 'info':
            self.units['leds']['led2'].blink(1, 1, 2)
        elif msg_type == 'warning':
            self.units['leds']['led2'].blink(2, 1, 3)
        elif msg_type == 'error':
            self.units['leds']['led2'].blink(1, 1, 10)

    def _report_on_topic(self, report):
        """Отправка отчёта посреднику по указанной теме.

        Рапортирование сопровождается световой индикацией.

        Параметры:
            :dict report: — объект компонента, осуществляющего отправку отчётов
        от своего имени через реализацию словаря с данными.
        """

        topic = '%s/%s/%s/%s/%s' % (
            str(self.ident),
            'report',
            report['to'],
            report['from'],
            report['report']['type']
        )
        payload = report['report']['body']

        self.units['leds']['led1'].on()
        self.client.publish(topic, payload, qos=2, retain=True)
        self.units['leds']['led1'].off()

    # def connection_maintenance(self):
    #     """Поддержание соединения с посредником.

    #     Делать попытки подключения к посреднику через установленный временной интервал,
    #     пока соединение не будет установлено.
    #     """

    #     pause = 30

    #     while not self.is_connected:
    #         try:
    #             self.client.connect(
    #                 self.broker,
    #                 self.port,
    #                 self.keepalive)
    #         except Exception as e:
    #             self.logger.error(
    #                 'Проблемы с подключением к %s! [%s]', self.broker, e)

    #         sleep(pause)

    # def ping(self):
    #     """Доклад о текущем состоянии."""

    #     pause = self.keepalive

    #     while True:
    #         sleep(pause)

    #         log_and_report(self, 'Онлайн', msg_type='info')

    # def disconnect(self):
    #     self.service.quit()
    #     self.client.disconnect()
