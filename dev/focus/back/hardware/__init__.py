import os
import yaml
from datetime import datetime

from .FocusSocket import FocusSocket, FocusLED
from .FocusReceptor import FocusReceptor, BaseUnit
from .FocusSocketControl import FocusSocketControl
from .FocusTemperature import FocusTemperature
from .FocusVoltage import FocusVoltage
from ..logger import Logger
from ..utils import CONFIG_FILE, LOG_FILE, DB_FILE
from ..utils.db_handlers import init_db, set_config, set_initial_gpio_status
from ..utils.messaging_tools import log_and_report


class Hardware:
    """Оборудование.

    Разбито на именованные группы.
    """

    def __init__(self, config_file=CONFIG_FILE):
        try:
            self.config = self.get_config(config_file)
            self.id = self.config['device']['id']

            # Головной регистратор:
            self.logger = Logger(LOG_FILE, prefix=self.id).instance

        except:
            msg_body = 'ошибка конфигурирования в файле [%s]' % config_file
            print(msg_body)

            raise

        # Создание словаря компонентов с именами классов в качестве значений.
        self.make_units_dict()

        # Инициализация локальной БД для записи необходимой информации и
        # управления устройством.
        self.conn = init_db(DB_FILE)
        set_config(self.conn, self.config)

        cursor = self.conn.cursor()
        set_initial_gpio_status(cursor, self.units)
        cursor.close()

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

    def make_units_dict(self):
        """Создать словарь компонентов на основе словаря конфигурации."""

        self.units = {}

        for group in self.config['units']:
            self.units[group] = self._set_context(self.config['units'][group])

    def _set_context(self, family: dict):
        """Установить контекст для компонентов единой группы.

        Параметры:
          :param family: — семейство компонентов устройства.
        """

        interface = eval(family.pop('class', None))

        if interface:
            ctx = {unit: interface(id=unit, **family[unit]) for unit in family}
        else:
            ctx = {
                'volt': FocusVoltage(id='volt', **family['volt']),
                # 'block': FocusBlockage(id='block', **family['block']),
            }

        return ctx

    @property
    def prefix(self):
        return self.prefix

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
