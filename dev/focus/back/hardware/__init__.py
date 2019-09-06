import os
import shelve
import uuid
from datetime import datetime
from typing import Any, Type

import yaml

from ..feedback.Logger import Logger
from ..utils import BACKUP_FILE, CONFIG_FILE, DB_FILE, LOG_FILE, MAPPING_FILE
from ..utils.concurrency import run_async

# from .FocusLED import FocusLED
# from .FocusReceptor import FocusReceptor
# from .FocusSocketControl import FocusSocketControl
# from .FocusTemperature import FocusTemperature
# from .FocusVoltage import FocusVoltage


class Hardware:
    """Оборудование.

    Разбито на именованные группы.
    """

    def __init__(self, config_file=CONFIG_FILE, backup_file=BACKUP_FILE):
        self.logger = Logger(LOG_FILE).instance

        msg_body = f'Подготовка оборудования...'
        self.logger.info(msg_body)

        try:
            self.config = self.get_config(config_file, backup_file)
        except:
            msg_body = 'Не удалось сконфигурировать оборудование!'
            self.logger.error(msg_body)

            raise

        with shelve.open(MAPPING_FILE) as db:
            db.update(self._make_units_dict(db), self._make_complects_dict(db))

    def get_config(self, config_file: str, backup_file: str) -> dict:
        """Загрузка описателя оборудования из файла конфигурации.

        Параметры:
          :param config_file: — название основного конфигурационного файла;
          :param backup_file: — название резервного конфигурационного файла,
        который будет использован в случае возникновения проблем с чтением
        данных из основного.

        Вернуть словарь конфигурации.
        """

        with open(config_file) as f:
            config = yaml.safe_load(f)

        return config if config else yaml.safe_load(backup_file)

    def _make_units_dict(self, db_mapping_file: shelve.Shelf) -> dict:
        """Создать словарь одиночных компонентов на основе словаря
        конфигурации.

        Параметры:
          :param db_mapping_file: — файл БД, содержащий полный набор классов,
        используемых для привязки конкретной модели к соответствующему семейству
        по ключу словаря.

        Вернуть словарь одиночных компонентов.
        """

        self.units = {}

        for family, children in self.config['units'].items():
            mapping = db_mapping_file[family]
            self.units[family] = self._set_context(family, children, mapping)

        return self.units

    def _make_complects_dict(self, db_mapping_file: shelve.Shelf) -> dict:
        """Создать словарь составных компонентов на основе словаря
        конфигурации.

        Параметры:
          :param db_mapping_file: — файл БД, содержащий полный набор классов,
        используемых для привязки конкретной модели к соответствующему семейству
        по ключу словаря.

        Вернуть словарь составных компонентов.
        """

        self.complects = {}

        for family, children in self.config['complects'].items():
            mapping = db_mapping_file[family]
            self.complects[family] = self._set_context(
                family, children, mapping)

        return self.complects

    def _set_context(
            self, family: str, children: dict, mapping: Type[Any]) -> dict:
        """Установить контекст для компонентов единого семейства.

        Параметры:
          :param family: — семейство компонентов устройства;
          :param children: — компоненты для установки контекста;
          :param mapping: — класс, к которому привязываются компоненты,
        реализуя единую объектную модель.

        Вернуть объект контекста в виде словаря.
        """

        ctx = {
            sibling: mapping(
                id=sibling, postfix=sibling[-1], **children[sibling]
            ) for sibling in children
        }

        return ctx

    @property
    def couts(self) -> dict:
        """Комплекты [Выход — Контроль]."""

        return self.complects['couts']

    @property
    def indicators(self) -> dict:
        """Индикаторы."""

        return self.units['leds']

    @property
    def inputs(self) -> dict:
        """Входы."""

        return self.units['ins']

    @property
    def temperature(self) -> dict:
        """Температура."""

        return self.units['temp']

    @property
    def misc(self) -> dict:
        """Уникальные компоненты."""

        return self.units['misc']
