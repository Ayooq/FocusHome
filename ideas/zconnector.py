#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Организация межпроцессорного обмена. Обеспечение обмена между головным демоном
прибора и его подсистемами. Головной демон прибора обеспечивает обмен с
прибором по протоколу SCPI. Подсистемы обеспечивают требуемую функциональность
прибора в составе РАБОЧЕГО МЕСТА.
Соединители (Connector) организуют связь между подсистемами и
головным демоном прибора по приему/передачи информации а так же
позволяют производить:
- сквозной обмен с подсистемами командами SCPI
- обмен с подсистемами сообщениями по формату ACTION/REPORT

'''
import logging
from threading import Thread

from zservice import ZSink
from zservice import ZServer


class Worker(object):
    '''Базовый организатор обмена
    Запускает обмен как поток. Устанавливает обработчик принятых сообщений
    '''
    def __init__(self, worker):
        self.logger = logging.getLogger('cfactory.%s' % __name__)
        self.receiver_thread = Thread(target=worker)
        self.receiver_thread.setDaemon(1)
        self.receiver_thread.start()

    def set_message_callback(self, callback):
        """Установить обработчик сообщения"""
        self.message_received = callback

    def message_received(self, message):
        """Обработчик сообщения по умолчанию"""
        raise NotImplementedError("Message callback not set")

    def quit(self):
        self.receiver_thread.join()


# TODO: Не откорректировано! Привести по аналогии с Connector
class ConnectorA(Worker):
    '''Соединитель ПОДCИСТЕМ УПРАВЛЕНИЯ
    Только принимает рапорты (PUSH/PULL). Распоряжения выдаются по подписке
    '''

    def __init__(self, **kwargs):
        self.server = ZSink(**kwargs)
        super(ConnectorA, self).__init__(self.worker)

    def publish(self, instruction):
        '''Выдача РАСПОРЯЖЕНИЙ по подписке
        :param instruction: Тело распоряжения
        '''
        # TODO: Проверка на Report
        topic = instruction.get('to', 'all')
        # msg = {'action': action}
        self.server.publish(topic, instruction)

    def worker(self):
        ''' Организатор ОБМЕНА
            Только ВЫТЯГИВАЕМ сообщения
        '''
        while True:
            message = self.server.receiver.recv_json()
            # print 'conw got -', message
            self.message_received(message)


# class Connector(Worker):
class Connector(object):
    ''' Соединитель ПРИБОРа c РАБМЕСТОМ
    Аргументы:
        :param: Уникальное имя коннектора
        :param `address`: Порт приема ЗАПРОС/ОТВЕТ
        :param `sink`: Порт выдачи инициативных событий
        :param `publish`: Порт приема сигналов управления
    '''

    def __init__(self, name, **kwargs):
        self.logger = logging.getLogger('cfactory.%s' % __name__)
        self.name = name        # Уникальное имя коннектора
        self.action_stack = []  # Список принятых АКТОВ
        self.server = ZServer(topic=self.name, **kwargs)  # сервер обмена

    def subscribe(self, name):
        '''Регистрация на дополнительный топик для подписки'''
        self.server.subscribe(name)

    def set_command_callback(self, callback):
        """Установить функцию приема КОМАНД"""
        self.command_received = callback

    def command_received(self, message):
        """Функция приема КОМАНД по умолчанию"""
        raise NotImplementedError("Сommand callback not set")

    def set_order_callback(self, callback):
        """Установить функцию приема ПРИКАЗОВ"""
        self.order_received = callback

    def order_received(self, message):
        """Функция приема ПРИКАЗОВ по умолчанию"""
        topic, order = message
        # raise NotImplementedError("Order callback not set")

    def set_display_error_callback(self, callback):
        '''Установить функцию отображения ошибок'''
        self.display_error = callback

    def display_error(self, err):
        '''Функция отображения ошибок по умолчанию'''
        print('Error!', str(err))

    def worker_easy(self):
        '''Простой организатор ОБМЕНА только командами'''
        self.logger.info(
            u'%s Хочу работать' %
            (self.worker_easy.__doc__)
        )
        while True:
            message = self.server.receive()
            self.logger.debug(
                u'%s Получил [%s]' %
                (self.worker_easy.__doc__, message)
            )
            try:
                response = self.command_received(message)
            except NotImplementedError as e:
                response = 'Error! %s' % e
            self.server.replay(response)

    def worker(self):
        ''' Организатор ОБМЕНА
        Каждая ветка ВИСИТ до ЗАВЕРШЕНИЯ своих обработчиков
        '''
        while True:
            try:
                self.server.wait()
            except KeyboardInterrupt:
                break

            # Основная ветвь КОМАНД строгий ЗАПРОС/ОТВЕТ
            if self.server.it_is_command:
                message = self.server.receive()
                try:
                    response = self.command_received(message)
                except NotImplementedError as e:
                    # TODO: Слабая спецификация. Связать с EasyCmd
                    response = 'Error! %s ' % e
                self.server.replay(response)  # Всегда ответ

            # Сигнальная ветвь только прием приказов
            if self.server.it_is_order:
                try:
                    message = self.server.get()
                    self.order_received(message)
                # except NotImplementedError as e:
                except Exception as e:
                    self.display_error(e)
                    continue


if __name__ == '__main__':
    from logger import create_logger
    import sys

    try:
        symbol = sys.argv[1]
    except Exception:
        symbol = 'd'

    # Это общий сигнальный обмен PUSH/POOL
    connecta = {  # Привязка к аргументам ZSink (zservice.py)
        'publish': 'ipc:///tmp/ikra-order.ipc',   # Распоряжения
        'sink': 'ipc:///tmp/ikra-report.ipc'  # Отчеты
    }

    pribor_address = {  # демон ПРИБОРА  ЗАПРОС/ОТВЕТ
        'address': "ipc:///tmp/ikra-instrument1.ipc"
    }
    '''Для прибора полный адрес'''
    pribor_address.update(connecta)

    logger = create_logger('DEBUG')

    if 'd' in symbol:
        logger.info('start demon')
        prb = Connector('fedor', **pribor_address)
        # prb.worker_easy()
        prb.worker()
        prb.subscribe(prb.name)
        logger.info('finish demon')
    else:
        pass
