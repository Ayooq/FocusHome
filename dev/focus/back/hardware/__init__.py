"""Модуль регистрации оборудования.

:class Hardware: класс привязки компонентов к физической раскладке устройства.
"""
import dbm
import shelve
from typing import Type

import yaml

from ..feedback import Logger
from ..utils import BACKUP_FILE, CONFIG_FILE, DB_FILE, LOG_FILE, MAPPING_FILE
from ..utils.messaging import notify
from .base import FocusBase


ShelveDB = shelve.DbfilenameShelf


class Hardware:
    """Оборудование."""

    def __init__(
            self,
            config_file: str = CONFIG_FILE,
            backup_file: str = BACKUP_FILE,
            log_level: int = 10
    ) -> None:
        self.logger = Logger(LOG_FILE, log_level).root

        msg = 'установка оборудования...'
        notify(self, msg, no_repr=True, local_only=True)

        try:
            self.config = self._get_config(config_file, backup_file)
        except IOError:
            msg = 'не удалось загрузить конфигурационные файлы!'
            notify(self, msg, no_repr=True, local_only=True)

            raise

        try:
            db = shelve.open(MAPPING_FILE, 'r')
        except dbm.error:
            db = self.__register_hardware()
        finally:
            self.hardware = self._make_hardware_dict(self.config, db)
            db.close()

    @staticmethod
    def _get_config(config_file: str, backup_file: str) -> dict:
        try:
            f = open(config_file)
        except FileNotFoundError:
            f = open(backup_file)
        finally:
            config = yaml.safe_load(f)
            f.close()

        return config

    def _make_hardware_dict(
            self, config: dict, mapping_file: ShelveDB) -> dict:
        res = {}

        for group, families in config.items():
            if group not in ('units', 'complects'):
                continue

            res[group] = {}

            try:
                misc = families.pop('misc')
            except KeyError:
                pass
            else:
                # Реструктурировать словарь для корректной привязки уникальным
                # компонентам соответствующих им классов:
                for k, v in misc.items():
                    families.update({k: {k: v}})

            for family, components in families.items():
                res[group][family] = {}

                if group == 'units':
                    mapping = mapping_file[group][family]
                    res[group][family] = self._set_context(components, mapping)
                elif group == 'complects':
                    for unit, data in components.items():
                        if res[group][family].get(unit):
                            continue

                        if 'src' in data:
                            src = data['src']

                            try:
                                data['src'] = res[group][family][src]
                            except KeyError:
                                src_mapping = mapping_file[group][family][src[:-1]]
                                src_data = components[src]
                                data['src'] = src_mapping(id=src, **src_data)
                                res[group][family][src] = data['src']

                        mapping = mapping_file[group][family][unit[:-1]]
                        res[group][family][unit] = mapping(id=unit, **data)

        return res

    @staticmethod
    def _set_context(components: dict, mapping: Type[FocusBase]) -> dict:
        ctx = {
            unit: mapping(id=unit, **data) for unit, data in components.items()
        }

        return ctx

    @classmethod
    def __register_hardware(cls) -> ShelveDB:
        from .autonomous import (
            FocusExternalReceptor as ExtR,
            FocusSocketControl as SockCtrl,
            FocusTemperatureSensor as T,
            FocusVoltageControlSingleton as V,
        )
        from .switchables import (
            FocusLEDIndicator as LED,
            FocusSocket as Sock,
            FocusSocketLockingSingleton as Lock,
        )

        db = shelve.open(MAPPING_FILE, 'n')
        db['units'] = {
            'leds': LED,
            'lock': Lock,
            'ins': ExtR,
            'temp': T,
            'volt': V,
        }
        db['complects'] = {
            'couts': {
                'out': Sock,
                'cnt': SockCtrl,
            },
        }

        return db

    @property
    def couts(self) -> dict:
        """Комплекты контролируемых выходов.

        :return: комплекты из двух компонентов: выход (ключ "out") и контроль
            (ключ "cnt")
        :rtype: dict
        """
        return self.hardware['complects']['couts']

    @property
    def indicators(self) -> dict:
        """Световые индикаторы.

        :return: индикаторы устройтва
        :rtype: dict
        """
        return self.hardware['units']['leds']

    @property
    def inputs(self) -> dict:
        """Входы.

        :return: рецепторы внешнего воздействия
        :rtype: dict
        """
        return self.hardware['units']['ins']

    @property
    def locking(self) -> Type[FocusBase]:
        """Блокировка.

        :return: компонент блокировки выходов
        :rtype: Type[FocusBase]
        """
        return self.hardware['units']['lock']['lock']

    @property
    def temperature(self) -> dict:
        """Температурные датчики.

        :return: датчики температуры
        :rtype: dict
        """
        return self.hardware['units']['temp']

    @property
    def voltage(self) -> Type[FocusBase]:
        """Напряжение.

        :return: компонент контроля напряжения в сети
        :rtype: Type[FocusBase]
        """
        return self.hardware['units']['volt']['volt']
