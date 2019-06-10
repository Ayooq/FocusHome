import os
import yaml

from . import (FocusLED, FocusReceptor, FocusSocket,
               FocusSocketControl, FocusTemperature)
from ..logger import Logger
from ..utils import CONFIG_FILE, LOG_FILE, DB_FILE
from ..utils.db_handlers import init_db, set_config
from ..utils.messaging_tools import log_and_report


class Hardware:
    """Оборудование.

    Разбито на именованные группы.
    """

    def __init__(self, config_file=CONFIG_FILE):

        # Головной регистратор:
        self.logger = Logger(LOG_FILE).instance

        # Заполнение словаря конфигурации на основе переданного файла.
        try:
            self.config = self.get_config(config_file)
        except Exception as e:
            msg_body = 'Ошибка в конфигурировании оборудования! [%s] [%s]' % (
                config_file, e)
            log_and_report(self, msg_body, msg_type='error')

            raise

        # Инициализация локальной БД для записи необходимой информации и
        # управления устройством.
        self.conn = init_db(DB_FILE)
        set_config(self.conn, self.config)

        # Создание словаря компонентов с именами классов в качестве значений.
        self.make_units_dict()

    def get_config(self, config_file):
        """Загрузка описателя оборудования из файла конфигурации.

        Конфигурационный файл должен быть доверительно проверен!
        Ссылки на имена классов позволяют выполнять произвольный код.
        """

        with open(config_file) as f:
            config_dict = yaml.load(f)

        return config_dict

    def make_units_dict(self):
        """Создать словарь компонентов на основе словаря конфигурации."""

        self.units = {}

        for group in self.config['units']:
            self.units[group] = self._set_context(self.config['units'][group])

    def _set_context(self, group):
        """Установить контекст для компонентов единой группы."""

        group.pop('description', 'Нет описания')

        try:
            component = eval(group.pop('class', None))
            ctx = {unit: component(
                ident=unit, **group[unit]) for unit in group}
        except Exception:
            raise

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
