# -*- coding: utf-8 -*-
''''
Конфигурационные файлы.

Конфигурация рабочего места для группы приборов и конфигурационные файлы
отдельных приборов.

Конфигурация рабочего места задается как справочник описателей инструментов.
Каждому описателю инструмента на рабочем месте присвоен уникальный ключ.
За описателем инструмента закреплен прибор в той или иной конфигурации.

конфигурация прибора состоит из:
- регистров управления (могут отсутствовать).
- набора команд прибора разбитых на подсистемы

Описатель инструмента является секцией файла конфигурации или в терминах
YAML - нодой (узлом).
Описатель инструмента состоит из класса инструмента и универсального
адреса (URI). Описатель инструмента должен быть для каждого применяемого
инструмента.
Пример описателя инструмента ddg::

    ddg:
        class: !!python/name:instruments.srs.SRSDG645
        uri: gpib+usb://COM7/15

Загрузка инструмента из этой конфигурации даст результат в виде словаря
следующей формы

`{'ddg': instruments.srs.SRSDG645.open_from_uri('gpib+usb://COM7/15')}`.

Для загрузки только одной части файла конфигурации нужно указать путь внутри
данного файла. Например, рассмотрим конфигурацию::

    instruments:
        ddg:
            class: !!python/name:instruments.srs.SRSDG645
            uri: gpib+usb://COM7/15
    prefs:
        ...

Если задать `"/instruments"` как конфигурационный путь, то в этом случае
функции загрузит инструменты описаные в этом блоке, и проигнорирует все
другие ключи в этом файле YAML.
'''

import os
import yaml

import logging


class IkraConfig(object):
    '''Загрузка конфигурации'''

    def __init__(self, name=None, workspace=[], node=None):
        self.logger = logging.getLogger('cfactory.%s' % __name__)
        self.name = name            # имя конфигурации
        self.workspace = workspace  # список вложености каталогов
        self.config = {}            # Словарь конфигурации
        self.load(node)

    def get_sub(self, key):
        u'''Найти подраздел или элемент по составному ключу
        :param key: ключ как строка полного пути или как список или кортеж
        Если ключ отсутствует возбуждается исключение KeyError
        '''
        return self._walk_dict(self.config, key)

    def _walk_dict(self, d, path):
        u""" Рекурсивный поиск в вложенным словарям по составному ключу
        :param d: Словарь с вложенными словарями
        :param path: Путь к элементу вложенного словаря
        :type path: `str` или `list` или `tuple`
        Пример :
        Дан словарь ``{'a': {'b': 42, 'c': {'d': ['foo']}}}`,
        Если задан path = ``"/"`` то возврат будет весь словарь
        Если задан path = ``"/a"`` возврат ``{'b': 42, 'c': {'d': ['foo']}}``
        Если задан path = ``/a/c/d"`` возврат ``['foo']``.
        Если ``path`` задан как список , это будет аналогично вызову
        ``"/" + "/".join(path)``.

        Если ключ не найден возбуждается исключение KeyError
        """
        # Если path is не указан вернем весь словарь.
        if not path:
            return d
        if isinstance(path, str):
            path = path.split("/")
        if not path[0]:
            # If the first part of the path is empty, do nothing.
            return self._walk_dict(d, path[1:])
        else:
            # Otherwise, resolve that segment and recurse.
            return self._walk_dict(d[path[0]], path[1:])

    def load_configure(self, conf_file_name, node_path="/"):
        u""" Загрузка описатель из файла конфигурации.

        :param str conf_file_name: имя файла конфигурации для загрузки
        :param str node_path: ``"/"`` путь секции в файле конфигуции.
        :rtype: `dict`

        .. warning::
            The configuration file must be trusted, as the class name references
            allow for executing arbitrary code. Do not load instruments from
            configuration files sent over network connections.

        Note that keys in sections excluded by the ``node_path`` argument are
        still processed, such that any side effects that may occur due to
        such processing will occur independently of the value of ``node_path``.

        Обратите внимание, что ключи в разделах, которые исключенны аргументом
        `node_path`, существуют и также будут обрабатываются.
        Так что могут возникнуть любые побочные эффекты, независимо от значения
        аргумента`node_path`
        """
        with open(conf_file_name, 'r') as f:
            conf_dict = yaml.load(f)
        conf_dict = self._walk_dict(conf_dict, node_path)
        return conf_dict

    def _ikra_path(self, subdirs, name):
        u'''Подготовить полное имя файла конфигурации.

         Имя подготавливается относительно переменной окружения `IKRAPATH`
        :param subdirs список вложености каталогов файла конфигурации
        :type subdirs: `tuple` или `list`
        :param name: имя файла конфигурации без расширения
        :return: полное имя файла конфигурации
        '''
        conf = name + '.yaml'
        path_list = [os.environ['IKRAPATH']]
        for p in subdirs:
            path_list.append(p)
        path_list.append(conf)
        conf_file_name = os.path.join(*path_list)
        return conf_file_name

    def load(self, node):
        u'''Загрузка описателя'''
        file_name = self._ikra_path(self.workspace, self.name)
        self.logger.debug(u'%s [%s]' % (self.load.__doc__, file_name))
        try:
            self.config = self.load_configure(file_name, node)
        except Exception as err:
            self.logger.debug(u'Ошибка! %s [%s] [%s]' %
                        (self.load.__doc__, file_name, err)
                    )
            raise

## Коллекция разных вариатов загрузок
##TODO: Формализовать допустимые каталоги


def get_instrument(name_instument):
    ''' Получить описатель инструмента из описателя рабочего места
        :param name_instument: условное имя инструмента
        :return: справочник конфигурации
        :rtype: dict
    '''
    node = '/instruments' + '/' + name_instument
    cfg = IkraConfig('workplace', ('etc',), node)
    return cfg.config


class Loader(IkraConfig):
    '''Загрузчик описателей оборудования'''

    def __init__(self, pribor_name, name, node=None):
        equipment_path = ['equipments', pribor_name, 'data']
        super(Loader, self).__init__(name, equipment_path, node)

    @property
    def header(self):
        ''' Полный заголовок как словарь'''
        h = self.config.get('header', u'нет заголовка')
        return h

    @property
    def topic(self):
        ''' Полное описание как словарь'''
        t = self.config.get('topic', u'нет описания')
        return t


class Equipment(object):
    ''' Загрузить описатели прибора
    :param name: имя прибора
    '''

    def __init__(self, name):
        self.name = name

    def _load(self, what, node_path):
        cfg = Loader(self.name, what, node_path)
        return cfg.config

    def status(self, node_path='/'):
        ''' Загрузить описатель регистров прибора'
        :param node_path: ``"/"`` путь секции в файле конфигуции для загрузки
        :return: справочник регистров
        :rtype: dict
        '''
        return self._load('status', node_path)

    def subsystem(self, node_path='/'):
        ''' Загрузить общий описатель подсистем прибора'
        :param node_path: ``"/"`` путь секции в файле конфигуции для загрузки
        :return: справочник подсистем
        :rtype: dict
        '''
        return self._load('subsystem', node_path)


#### Секция групповой загрузки приборов ###
##TODO: Отестировать! Должно быть в start.py


def open_inst(value):
        try:
            instr = value["class"].open_from_uri(value["uri"])
            instr.configfile = value["config"]  # Добавим имя конфигурации
            return instr
        except:
            raise


if __name__ == '__main__':
    import sys
    from candle.logger import create_logger

    logger = create_logger()
    workplace = 'workplace'
    logger.info(u'начало работы')
    try:
        pribor_name = sys.argv[1]    # Условное имя прибора
    except:
        pribor_name = 'G1'
    # Попытки загрузить именнованый описатель рабочего места
    #try:
    logger.info(u'загрузка описателя рабочего места')
    wrk = IkraConfig(
        workplace,
        ('etc', )    # Одиночный каталог завершается запятой
        #['instruments', pribor_name]
    )
    #except Exception as err:
        #msg = u'Ошибка! загрузки конфигурации для %s [%s]' % (workplace, err)
        #logger.error(msg)
        #logger.critical(u'завершение')
        #sys.exit(1)

    ##msg = u'%s' % u', '.join(wrk.header)
    #msg = 'test'
    #logger.info(u'конфигурация рабочего места %s [%s]загружена' %
                #(workplace, msg)
            #)

    ## Проверка на наличие прибора на рабочем месте
    #try:
        #kwargs_prb = wrk.get_sub(['instruments', pribor_name])
    #except Exception as err:
        #msg = u'Ошибка! Прибора %s нет в составе раб.места ' % pribor_name
        #logger.error(msg)
        #logger.critical(u'завершение')
        #sys.exit(1)

    #ident_pribor = kwargs_prb.get('ident', u'не указан')
    #logger.info(u'конфигурация прибора %s [%s] определена' %
                #(pribor_name, ident_pribor)
            #)
    ## Проверка конфигурации прибора
    #eq = Equipment(ident_pribor)
    #try:
        #status_cfg = eq.status()
        #logger.info(u'%s. Конфигурация регистров загружена' % ident_pribor)
    #except Exception as err:
        #msg = u'Описатель регистров прибора %s [%s]' % (ident_pribor, err)
        #logger.error(msg)

    #try:
        #subs_cfg = eq.subsystem()
        #logger.info(u'%s. Конфигурация подсистем загружена' % ident_pribor)
    #except Exception as err:
        #msg = u'Описатель подсистем прибора %s [%s]' % (ident_pribor, err)
        #logger.error(msg)
    ## Далее можно вызывать  pribor  с аргументами словаря prb
#