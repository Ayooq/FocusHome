import json
from time import sleep
from datetime import datetime
from threading import Thread

import paho.mqtt.client as mqtt


from .hardware import Hardware
from .reporting import Reporter
from .utils import DB_FILE
from .utils.concurrency import Worker
from .utils.db_handlers import init_db, get_device_id, define_broker, fill_table
from .utils.messaging_tools import register, log_and_report


class Connector(Hardware):
    """Обвязка функционала MQTT вокруг :class Hardware: без учета авторизации."""

    def __init__(self, **kwargs):
        super().__init__()

        self.pin = None
        self.description = self.config['device']['location']

        self.conn = init_db(DB_FILE, self.config, self.units)
        self.id = get_device_id(self.conn)
        self.broker, self.port, self.keepalive = define_broker(self.conn)

        self.reporter = Reporter(self.id)
        self.register_device(self.blink_on_report, self.report_on_topic)

        self.client = mqtt.Client(self.id, False)
        self.client.on_connect = self.on_connect
        # self.client.on_message = self.on_message
        LWT = self.set_status_message('offline', qos=1)
        self.client.will_set(**LWT)

        msg_body = 'starting %s' % self.id
        log_and_report(self, msg_body, msg_type='info')

        self.is_connected = False
        # self.establish_connection(3)
        self.client.connect(self.broker, self.port, self.keepalive)

        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc:
            log_and_report(self, rc, msg_type='error')
        else:
            self.is_connected = True
            status = self.set_status_message('online')
            client.publish(**status)

            # Подписка на акции.
            client.subscribe(self.id + '/action/#', qos=2)

    def on_disconnect(self, client, userdata, rc):
        self.is_connected = False

        if rc:
            log_and_report(self, rc, msg_type='error')

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

    def register_device(self, *callbacks):
        """Зарегистрировать устройство и его компоненты для рапортирования.

        Отправка отчётов осуществляется по трём каналам:
        1) каждое событие регистрируется подсписчиком "blink", который
        осуществляет световую индикацию, основанную на типе события;
        2) события, связанные с взаимодействием устройства и посредника,
        записываются на имя "dev" от имени самого устройства;
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
        register(self, 'dev', callbacks[1])

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

    def set_status_message(self, msg, qos=0, retain=True):
        """Определить сообщение о статусе устройства для отправки посреднику.

        Параметры:
          :param msg: — тело сообщения в виде строки состояния;
          :param qos: — уровень доставки сообщения посреднику, от 0 до 2;
          :param retain: — булевый показатель сохранения сообщения в качестве
        последнего "надёжного", выдаваемого сразу при подписке на данную тему.

        Вернуть объект словаря для связывания с методом publish() клиента MQTT.
        """

        timestamp = datetime.now().isoformat(sep=' ')
        tabledata = {
            'event': (timestamp, msg),
            'status': (self.id, None, self.description)
        }
        print(tabledata)

        topic = '%s/status' % self.id
        payload = json.dumps(tabledata)

        return {
            'topic': topic,
            'payload': payload,
            'qos': qos,
            'retain': retain,
        }

    # def establish_connection(self, sec_to_wait: int):
    #     """Установить соединение с посредником.

    #     Делать попытки подключения до тех пор, пока связь не будет налажена.

    #     Параметры:
    #       :param sec_to_wait: — время в секундах, определяющее интервал
    #     между попытками подключения к посреднику.
    #     """

    #     while not self.is_connected:
    #         try:
    #             self.client.connect(
    #                 self.broker,
    #                 port=self.port,
    #                 keepalive=self.keepalive
    #             )
    #         except:
    #             msg_body = 'не удаётся установить связь с посредником'
    #             self.logger.error(msg_body)

    #         sleep(sec_to_wait)

    def blink_on_report(self, msg: dict):
        """Моргать при регистрации событий.

        Индикация производится следующим образом:
        1) event — светодиод включается на секунду, затем выключается,
        однократно;
        2) info — светодиод включается на секунду, отключается на одну, дважды;
        3) warning — светодиод включается на две секунды, отключается на одну,
        трижды;
        4) error — светодиод включается на одну секунду, выключается на одну,
        десять раз подряд.

        Параметры:
          :param msg: — объект компонента, осуществляющего отправку отчётов
        от своего имени через реализацию словаря с данными.
        """

        msg_type = msg[msg.topic]['msg_type']

        if msg_type == 'event':
            self.indicators['led2'].blink(1, 1, 1)
        elif msg_type == 'info':
            self.indicators['led2'].blink(1, 1, 2)
        elif msg_type == 'warning':
            self.indicators['led2'].blink(2, 1, 3)
        elif msg_type == 'error':
            self.indicators['led2'].blink(1, 1, 10)

    def report_on_topic(self, msg: dict):
        """Отправка отчёта посреднику по указанной теме.

        Рапортирование сопровождается световой индикацией.

        Параметры:
          :param msg: — объект отчёта, содержащий необходимые данные
        для формирования структуры результирующего сообщения.
        """

        publish_data = self._form_publish_data(msg)
        tabledata = self._form_tabledata(msg)
        publish_data['payload'] = json.dumps(tabledata)

        self.indicators['led1'].on()
        self.client.publish(**publish_data)
        self.indicators['led1'].off()

    def _form_publish_data(self, msg: dict):
        """Сформировать объект с данными для публикации отчёта.

        Параметры:
          :param msg: — объект отчёта, содержащий необходимые данные
        для формирования структуры результирующего сообщения.

        Вернуть объект словаря для связывания с методом publish() клиента MQTT.
        """

        report = msg[msg.topic]
        msg_type = report['msg_type']

        topic = '%s/%s/%s/%s/%s' % (
            self.id,
            msg.topic,
            msg['to'],
            msg['from'],
            msg_type,
        )
        payload = report['msg_body']
        qos = report['qos']
        retain = report['retain']

        return {
            'topic': topic,
            'payload': payload,
            'qos': qos,
            'retain': retain,
        }

    def _form_tabledata(self, msg: dict):
        """Сформировать объект табличных данных для отправки посреднику.

        Записать данные в локальную БД, а затем вернуть объект словаря с
        необходимыми значениями полей для заполнения БД на хосте посредника.

        Параметры:
          :param msg: — объект отчёта, содержащий необходимые данные
        для формирования структуры результирующего сообщения.
        """

        timestamp = datetime.now().isoformat(sep=' ')
        cursor = self.conn.cursor()
        tables_set = {'events'}
        result_dict = {}

        report = msg[msg.topic]
        msg_type = report['msg_type']
        msg_body = report['msg_body']
        
        if msg['from'] == self.id:
            msg['from'] = 'focuspro'

        tabledata = [timestamp, msg_type, msg['to'], msg['from'], msg_body]

        fill_table(self.conn, cursor, tables_set, tabledata)

        if msg['from'] != 'focuspro':
            pin = report['gpio'][0]
            description = report['gpio'][1]

            tabledata[1] = pin
            tabledata.insert(-1, description)

            tables_set.clear()
            tables_set.update({'gpio_status', 'gpio_status_archive'})

            fill_table(self.conn, cursor, tables_set, tabledata)

            result_dict['status'] = (
                self.id + '/' + msg['from'], tabledata[1], tabledata[-2]
            )

        result_dict['event'] = tabledata[0], tabledata[-1]

        return result_dict
