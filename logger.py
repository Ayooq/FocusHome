# -*- coding: utf-8 -*-
import logging

log_forms = [
u'%(asctime)s %(name)s %(levelname)s %(message)s',
u'%(filename)s[LINE:%(lineno)d] #%(levelname)-8s[%(asctime)s] %(message)s'
]


def create_logger(console_level=logging.INFO):
    u'''Создание головного регистратора'''

    # создать logger по имени 'c_factory'
    # logger = logging.getLogger('cfactory')
    # logger.setLevel(logging.INFO)
    # создать file handler для регистрации всех debug сообщений
    fh = logging.FileHandler('candle.log')
    fh.setLevel(logging.INFO)
    # создать  formatter и добавить его в handlers
    formatter = logging.Formatter(log_forms[0])
    # formatter = logging.Formatter(log_forms[1])
    fh.setFormatter(formatter)
    # add the handlers to the logger
    # logger.addHandler(fh)
    return  fh

def create_2_logger(console_level=logging.INFO):
    u'''Создание головного регистратора'''

    # создать logger по имени 'c_factory'
    logger = logging.getLogger('cfactory')
    logger.setLevel(logging.INFO)
    # создать file handler для регистрации всех debug сообщений
    fh = logging.FileHandler('candle.log')
    fh.setLevel(logging.INFO)
    # создать console handler
    ch = logging.StreamHandler()
    ch.setLevel(console_level)  # На период отладки
    # создать  formatter и добавить его в handlers
    eformatter = logging.Formatter(log_forms[1])
    formatter = logging.Formatter(log_forms[0])
    # formatter = logging.Formatter(log_forms[1])
    fh.setFormatter(formatter)
    ch.setFormatter(eformatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
