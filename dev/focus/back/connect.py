import json
from time import sleep
from threading import Thread

import paho.mqtt.client as mqtt

from .hardware import Layout, log_and_report
from .report import Reporter
from .utils import Worker


class Connector(Layout):
    """Обвязка функционала MQTT вокруг :class Layout: без учета авторизации."""

    def __init__(self, **kwargs):
        super().__init__()

        self.description = self.config['device']['description']

        self.set_broker(**self.config['device']['broker'])

        self.client_id = kwargs.pop('id', str(self.ident))
        self.client = mqtt.Client(self.client_id)

        # Регистрация функций обработки.
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.reporter = Reporter(self.ident)

        self.register_lamp(self.blink)
        self.register_units(self.report_on_topic)
        self.register('alive', self.report_on_topic)

        Worker(self.establish_connection)
        Worker(self.ping)

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
            self.logger.error(
                'В соединении с %s отказано! Код ответа: [%s]', self.broker, rc)
        else:
            self.is_connected = True
            self.logger.info('Соединение с %s установлено.', self.broker)

            # Подписка на акции.
            self.client.subscribe(self.ident + '/action/#')

    def on_message(self, client, userdata, msg):
        self.logger.info('Инструкция %s [%s]', msg.topic, str(msg.payload))

        # Десериализация JSON запроса.
        data = json.loads(msg.payload)

        if data['method'] == 'getFocuspioStatus':
            # Вернуть статус FocusPIO.
            client.publish(
                msg.topic.replace('request', 'response'),
                #   get_gpio_status(), 1
            )
        elif data['method'] == 'setFocuspioStatus':
            # Обновить статус FocusPIO и отправить ответ.
            client.publish(
                msg.topic.replace('request', 'response'),
                #   get_gpio_status(), 1
            )
        #   client.publish(, get_gpio_status(), 1)

    def register_lamp(self, callback):
        """Зарегистрировать световой индикатор в роли подписчика."""

        for grouped_components in self.units.values():
            for unit in grouped_components:
                grouped_components[unit].register('lamp', callback)

    def register_units(self, callback):
        """Зарегистрировать все компоненты устройства для рапортирования."""

        for group_name, grouped_components in self.units.items():
            for unit in grouped_components:
                grouped_components[unit].register(group_name, callback)

    def register(self, subscriber, callback):
        self.reporter.register(subscriber, callback)

    def unregister(self, subscriber):
        self.reporter.unregister(subscriber)

    def blink(self, report):
        """Моргать при регистрации определённых событий."""

        msg_type = report['report']['type']
        if msg_type in ('event', 'warning', 'error'):
            self.units['indicators']['led2'].blink(1, 1, 1)

    def report_on_topic(self, report):
        """Отправка отчёта посреднику по указанной теме."""

        topic = '%s/%s/%s/%s/%s' % (
            str(self.ident),
            'report',
            report['to'],
            report['from'],
            report['report']['type']
        )
        payload = report['report']['body']
        self.units['indicators']['led1'].toggle()
        self.client.publish(topic, payload)
        self.units['indicators']['led1'].toggle()

    def establish_connection(self):
        """Установить соединение с посредником.

        Делать попытки подключения к посреднику через установленный временной интервал,
        пока соединение не будет установлено.
        """

        pause = 30

        while not self.is_connected:
            try:
                self.client.connect(
                    self.broker,
                    self.port,
                    self.keepalive)
            except Exception as e:
                self.logger.error(
                    'Проблемы с подключением к %s! [%s]', self.broker, e)

            sleep(pause)

    def ping(self):
        """Доклад о текущем состоянии."""

        pause = self.delta

        while True:
            sleep(pause)

            log_and_report(self, 'Focus', 'Онлайн', msg_type='info')

    def _del_(self):
        self.client.disconnect()
        self.quit()
