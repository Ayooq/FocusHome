#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Словарь сообщения для сериализации JSON
Разрешенные типы body
Python       JSON
dict         object
list, tuple  array
str          string
int, float   number
True         true
False        false
None         null
Проверять body по isinstance
'''

import json


class Event(object):
    def __init__(self):
        # <descript>Основные АВАРИИ</descript>
        # <event>
        # <name>connect</name>
        # <descript>Нет&# 13;соединения</descript>
        # <type>error</type>
        # <!-- Список ассоциированых акций-->
        # <action>
        # <name>pinit</name>
        # <image>put</image>
        # <descript>порт</descript>
        # </action>
        # <message>Cериальный ПОРТ не найден</message>
        # <message>Не правильно подключен кабель к компьютеру</message>
        # <message>Возможен отказ ПОРТА</message>
        # <message></message>
        # </event>
        pass


class Content(dict):
    '''Структура содержимого'''
    _subkeys = (
        'head',    # Заголовок
        'types',   # Тип
        'body'     # Тело
    )

    def __init__(self):
        super(Content, self).__init__()
        for key in Content._subkeys:
            self.setdefault(key)

    def inscribe(self, head, types, body):
        '''Вписать содержимое
        '''
        self['types'] = types  # Тип
        self['head'] = head    # Заголовок
        self['body'] = body    # Тело сообщения


class Paper(dict):
    ''' Типовое сообщение по виду
    '''
    def __init__(self, what_paper):
        super(Paper, self).__init__()
        self._content = what_paper
        self.setdefault(what_paper, Content())

    def _formalize(self, head, types, body):
        ''' Официально оформить содержимое
        '''
        b = self[self._content]
        b.inscribe(head, types, body)


class Report(Paper):
    ''' РАПОРТ по типам'''
    types = ['event', 'error', 'info', 'warning']

    def __init__(self, head=None, types=None, body=None, what='report'):
        super(Report, self).__init__(what)
        self._formalize(head, types, body)

    def event(self, head, body):
        'Событие'
        self._formalize(head, 'event', body)
        return self

    def error(self, head, body):
        'Ошибка'
        self._formalize(head, 'error', body)
        return self

    def info(self, head, body):
        'Информация'
        self._formalize(head, 'info', body)
        return self

    def warning(self, head, body):
        'Предупреждение'
        self._formalize(head, 'warning', body)
        return self

from datetime import datetime

class Address(dict):

    def __init__(self, from_it, to_it):
        super(Address, self).__init__()
        self['from'] = from_it   # Источник
        self['to'] = to_it   # Адресат
        now = datetime.today()
        self['date'] = now.strftime('%Y%m%d%H%M%S')

    def get(self, report):
        return (report.get('from', 'system'), report.get('to', 'anybody'))


class Reporter(Report):
    ''' Выдача РАПОРТа от имени через механизм
        Реализует паттерн МОДЕЛЬ
    '''

    def __init__(self, who, printer=None):
        self._from = str(who)    # От кого
        self._callbacks = {}  # Словарь функций оповещения
        super(Reporter, self).__init__()

    def registre(self, to, func):
        '''Добавить функцию оповещения
        Регистрация НАБЛЮДАТЕЛЯ

        :param to: Уникальное имя наблюдателя
        :param func: Функция оповещения на наблюдателе
        '''
        self._callbacks[to] = func

    def unregistre(self, to):
        '''Удалить функцию оповещения
        Удаления НАБЛЮДАТЕЛЯ

        :param to: Уникальное имя наблюдателя
        '''
        del self._callbacks[to]

    def _docallbacks(self):
        '''Оповещение НАБЛЮДАТЕЛЕЙ'''
        for to in self._callbacks:
            self.send(to, self)

    def send(self, to, report):
        '''Выдача подготовленого рапорта по адресу

        :param to: Уникальное имя наблюдателя
        :param report: Заранее подготовленый РАПОРТ
        '''
        adr = Address(self._from, to)
        report.update(adr)
        try:
            func = self._callbacks[to]
            return func(report)
        except:
            self.dumper(report)
            pass

    def public(self):
        '''широковещательная рассылка'''
        self._docallbacks()

    def dumper(self, doc):
        '''тестовый вывод'''
        print(u'Печатаю', json.dumps(doc, ensure_ascii=True))


if __name__ == "__main__":

    def what_functions(my_class):
        u"""Список методов"""
        attrs = [arg for arg in dir(my_class) if not arg.startswith('_')]
        print([arg for arg in attrs if callable(getattr(my_class, arg))])

    msg = Report(u'it is event', 'event', 'bla bla bla', 'action')
    print('simple report->', msg)
    print('other simple report->', msg.info('it is info', 'ta ta ta ata'))

    tutu = ['my events!', ['drink beer', 'Test dog', 'Sing song']]
    kuku = {'man': 'John', 'women': 'Marry'}
    # Создадим модель
    rpt = Reporter('goga')
    # print(dir(rpt))
    # Регистрируем наблюдателей с тестовой функцией оповещения
    rpt.registre('boba', rpt.dumper)
    rpt.registre('vova', rpt.dumper)
    # Выдадим всем наблюдателям
    print(u'Два наблюдателя-------------------------------------------')
    rpt.warning('List', tutu).public()
    # Исключим одного
    print(u'Один наблюдатель------------------------------------------')
    rpt.unregistre('boba')
    rpt.info('Dictant', kuku).public()
    print(u'send Выдача подготовленого рапорта по адресу. Без запоминания')
    msg.error('HITS!', u'Russian  vodka')
    rpt.send('vova', msg)
    print(u'last reports с новым наблюдателем ------------------------')
    rpt.registre('dodo', rpt.dumper)
    rpt.public()
    print('reporter -------------------')
    print(rpt)
