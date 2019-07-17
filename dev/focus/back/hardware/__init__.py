import os
import uuid
import yaml
from datetime import datetime

from .FocusSocket import FocusLED
from .FocusReceptor import FocusReceptor
from .FocusSocketControl import FocusSocketControl
from .FocusTemperature import FocusTemperature
from .FocusVoltage import FocusVoltage
from ..logger import Logger
from ..utils import CONFIG_FILE, LOG_FILE
from ..utils.messaging_tools import log_and_report


class Hardware:
    """Оборудование.

    Разбито на именованные группы.
    """

    _mapping = {
        'leds': FocusLED,
        'ins': FocusReceptor,
        'couts': FocusSocketControl,
        'temp': FocusTemperature,
        'misc': FocusVoltage,
    }

    def __init__(self, config_file=CONFIG_FILE):
        try:
            self.config = self.get_config(config_file)
            self.logger = Logger(LOG_FILE).instance
        except:
            msg_body = 'ошибка конфигурирования в файле [%s]' % config_file
            self.logger.error(msg_body) if self.logger else print(msg_body)

            raise

        self._make_units_dict()

    def get_config(self, config_file: str):
        """Загрузка описателя оборудования из файла конфигурации.

        Конфигурационный файл должен быть доверительно проверен!
        Ссылки на имена классов позволяют выполнять произвольный код.

        Параметры:
          :param config_file: — название конфигурационного файла.
        """

        with open(config_file) as f:
            config_dict = yaml.load(f)

        return config_dict

    def _make_units_dict(self):
        """Создать словарь компонентов на основе словаря конфигурации."""

        self.units = {}

        for family, children in self.config['units'].items():
            self.units[family] = self._set_context(family, children)

    def _set_context(self, family: str, children: dict):
        """Установить контекст для компонентов единого семейства.

        Параметры:
          :param family: — семейство компонентов устройства;
          :param children:

        Вернуть объект контекста в виде словаря.
        """

        class_ = Hardware._mapping[family]
        ctx = {
            sibling: class_(
                id=sibling, postfix=sibling[-1], **children[sibling]
            ) for sibling in children
        }

        return ctx

    @property
    def indicators(self):
        """Индикаторы."""

        return self.units['leds']

    @property
    def inputs(self):
        """Входы."""

        return self.units['ins']

    @property
    def complects(self):
        """Комплекты [Гнездо — Контроль состояния]."""

        return self.units['couts']

    @property
    def temperature(self):
        """Температура."""

        return self.units['temp']

    @property
    def misc(self):
        """Дополнительные компоненты."""

        return self.units['misc']
