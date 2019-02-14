#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import zmq
import logging

# Диапазон 49152—65535 содержит динамически выделяемые или частные порты.
# Эти порты используются короткоживущими соединениями «клиент — сервер»
# или в определенных частных случаях
WORK = 'tcp://127.0.0.1:55500'
SINK = 'tcp://127.0.0.1:55510'
PUBLISHER = 'tcp://127.0.0.1:55520'


class ZClient(object):
    '''Простой клиент ЗАПРОС/ОТВЕТ'''

    def __init__(self, **kwargs):
        self.logger = logging.getLogger('cfactory.%s' % __name__)
        self.address = kwargs.get('address', WORK)
        self.context = zmq.Context()
        # тип обмена Запрос/Ответ мы ЗАПРАШИВАЕМ
        self.requester = self.context.socket(zmq.REQ)
        rep = self.requester.connect(self.address)
        self.logger.debug(
                u'%s Connect to %s [%s]' %
                (self.worker_easy.__doc__, self.address, rep)
        )

    def reader(self, command):
        # TODO: Анализ кодов возврата
        # print 'wonna replay', command
        rep = self.requester.send(command)
        # print rep
        msg_in = self.requester.recv()
        return msg_in

    def __del__(self):
        self.requester.close()


class ZEasyServer(object):
    '''Простой сервер ЗАПРОС/ОТВЕТ
    '''
    def __init__(self, address=WORK):
        self.address = address
        self.context = zmq.Context()
        # метод обмена Запрос/Ответ Мы ОТВЕЧАЕМ
        self.replayer = self.context.socket(zmq.REP)
        self.replayer.bind(self.address)  # механизм TCP

    def __del__(self):
        self.replayer.close()


class Order(object):
    '''Рассылка/получение приказов
    Приказы рассылаются и читаются по подписке
    Формат приказов - json
    '''
    def __init__(self):
        self.topics = []

    def publish(self, socket, topic, order):
        '''Публикация приказа

            :param socket: сокет zmq. Должен быть типа zmq.PUB
            :param topic: тема подписки. Одно слово
            :param order: тело приказа. Словарь
        '''
        socket.send(topic, flags=zmq.SNDMORE)
        socket.controller.send_json(order)

    def read(self, socket):
        '''Считывание приказа по пoдписке

            :param socket: сокет zmq. Должен быть типа zmq.SUB
            :return: тема подписки, приказ
        '''
        topic = socket.recv()       # Подписанный ТОПИК
        order = socket.recv_json()  # Данные как СЛОВАРЬ
        return (topic, order)

    def subscribe(self, socket, topic):
        '''Подписка на рассылку приказов

            :param socket: сокет zmq. Должен быть типа zmq.SUB
            :param topic: тема подписки. Одно слово
        '''
        if isinstance(topic, str):
            if topic in self.topics:
                pass
            socket.setsockopt_string(zmq.SUBSCRIBE, topic)
            self.topics.append(topic)
        else:
            pass

    def unsubscribe(self, socket, topic):
        '''Отказ от подписки

            :param socket: сокет zmq. Должен быть типа zmq.SUB
            :param topic: тема подписки. Одно слово
        '''
        if isinstance(topic, str):
            if topic in self.topics:
                socket.setsockopt(zmq.UNSUBSCRIBE, topic)
                self.topics.remove(topic)
            else:
                pass
        else:
            pass

    def put(self, socket, message):
        '''Выдача события

        :param socket: сокет zmq
        :param message: Тело сообщение. Словарь
        '''
        socket.send_json(message)

    def get(self, socket):
        '''Простое считывание информации с сигнальной линии

            :param socket: сокет zmq
        '''
        topic = 'easy'
        data = socket.recv()
        return (topic, data)


class ZServer(object):
    '''Сервер ЗАПРОС/ОТВЕТ

        :param `address`: Порт приема ЗАПРОС/ОТВЕТ
        :param `push`: Порт выдачи инициативных событий
        :param `sub`: Порт приема сигналов управления
    '''
    def __init__(self, topic=b'test', **kwargs):
        self.logger = logging.getLogger('cfactory.%s' % __name__)
        self.address = kwargs.get('address', WORK)
        self.address_push = kwargs.get('sink', SINK)
        self.address_sub = kwargs.get('publish', PUBLISHER)

        self.context = zmq.Context()
        # Основная ветвь
        # метод обмена Запрос/Ответ Мы ОТВЕЧАЕМ
        self.replayer = self.context.socket(zmq.REP)
        self.replayer.bind(self.address)  # механизм TCP

        # Socket для СИГНАЛОВ управления
        self.controller = self.context.socket(zmq.SUB)
        self.controller.connect(self.address_sub)
        self.order = Order()
        self.order.subscribe(self.controller, topic)

        # Socket для выдачи СОБЫТИЙ
        self.pusher = self.context.socket(zmq.PUSH)
        self.pusher.connect(self.address_push)

        # Process messages from receiver and controller
        self.poller = zmq.Poller()
        self.poller.register(self.replayer, zmq.POLLIN)
        self.poller.register(self.controller, zmq.POLLIN)

    def wait(self):
        ''' Ожидание приема

        :replay: Словарь активных сокетов
        Здесь будем висеть пока что-нибудь не получем
        '''
        self._sockets = dict(self.poller.poll())
        return self._sockets

    @property
    def it_is_command(self):
        '''Проверка на сквозняк'''
        return self.replayer in self._sockets

    @property
    def it_is_order(self):
        '''Проверка на приказы'''
        return self.controller in self._sockets

    '''Тупые примитивы для сквозняка'''
    def receive(self):
        '''Ожидание сообщения'''
        message = self.replayer.recv()
        return (message)

    def replay(self, data):
        '''Ответ на принятое сообщение'''
        self.replayer.send(data)

    '''Сигнальные примитивы'''
    def subscribe(self, topic):
        '''Попытка подписаться на'''
        self.order.subscribe(self.controller, topic)

    def get(self):
        '''Считывание сигнала'''
        return (self.order.read(self.controller))

    def put(self, msg):
        '''Выдача события'''
        self.order.put(self.pusher, msg)

    def eget(self):
        '''Простое считывание информации с сигнальной линии
        '''
        return self.order.get(self.controller)

    def __del__(self):
        '''При удаление - закроем все сокеты'''
        try:
            self.replayer.close()
            if self.pusher:
                self.pusher.close()
            self.controller.close()
        except Exception as er:
            self.logger.error('%s' % er)


class ZSink(object):
    '''Сервер УПРАВЛЕНИЯ
        Принимает СООБЩЕНИЯ методу PUSH/PULL ТОЛКАЙ/ТЯНИ
        Результат выдается всем по ПОДПИСКЕ - аналог управления по СИГНАЛАМ
    '''
    def __init__(self, **kwargs):
        self.address_pull = kwargs.get('sink', SINK)
        self.address_pub = kwargs.get('publish', PUBLISHER)
        self.context = zmq.Context()
        # Socket  для входящих СООБЩЕНИЙ метод обмена ВЫТЯНУТЬ. Мы НЕ ОТВЕЧАЕМ
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.bind(self.address_pull)    # механизм TCP
        # Socket для СИГНАЛОВ управления метод ПУБЛИКАЦИЯ
        self.controller = self.context.socket(zmq.PUB)
        self.controller.bind(self.address_pub)

    def publish(self, topic, msg):
        self.controller.send(topic, flags=zmq.SNDMORE)
        self.controller.send_json(msg)

    def __del__(self):
        self.receiver.close()
        self.controller.close()
