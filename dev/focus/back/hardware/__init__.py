import os
import shelve
import uuid
from datetime import datetime
from typing import Any, Type

import yaml

from ..feedback import Logger
from ..utils import BACKUP_FILE, CONFIG_FILE, DB_FILE, LOG_FILE, MAPPING_FILE
from .locking import FocusLocking
from .voltage import FocusVoltage


class Hardware:
    """Оборудование.

    Свойства:
        :prop couts(self): — словарь экземпляров класса комплектов
    контролируемых выходов;
        :prop indicators(self): — словарь экземпляров класса световых
    индикаторов;
        :prop inputs(self): — словарь экземпляров класса входных рецепторов;
        :prop locking(self): — экземпляр класса блокировки выходов;
        :prop temperature(self): — словарь экземпляров класса температурных
    датчиков;
        :prop voltage(self): — экземпляр класса контроля питания устройства.
    """

    def __init__(
        self,
        config_file: str = CONFIG_FILE,
        backup_file: str = BACKUP_FILE,
        log_level: int = None
    ) -> None:
        self.logger = Logger(LOG_FILE)

        msg_body = 'Подготовка оборудования...'
        self.logger.info(msg_body)

        try:
            self.config = self._get_config(config_file, backup_file)
        except IOError:
            msg_body = 'Не удалось загрузить конфигурационные файлы!'
            self.logger.error(msg_body)

            raise

        with shelve.open(MAPPING_FILE, 'r') as db:
            self.units = self._make_components_group_dict(
                self.config['units'], db)
            self.complects = self._make_components_group_dict(
                self.config['complects'], db)

    def _get_config(self, config_file: str, backup_file: str) -> dict:
        try:
            f = open(config_file)
        except FileNotFoundError:
            f = open(backup_file)
        finally:
            config = yaml.safe_load(f)
            f.close()

        return config

    def _make_components_group_dict(
            self, group: dict, db_mapping_file: shelve.Shelf) -> dict:
        # Реструктурировать словарь для корректной привязки уникальным
        # компонентам соответствующих им классов:
        try:
            misc = group.pop('misc')
        except KeyError:
            pass
        else:
            for k, v in misc.items():
                group.update(
                    {
                        k: {
                            k: v,
                        },
                    },
                )

        res = {}

        for family, children in group.items():
            mapping = db_mapping_file[family]
            res[family] = self._set_context(children, mapping)

        return res

    def _set_context(self, children: dict, mapping: Type[Any]) -> dict:
        ctx = {
            sibling: mapping(
                id=sibling, postfix=sibling[-1], **children[sibling]
            ) for sibling in children
        }

        return ctx

    @classmethod
    def __register_hardware(cls) -> None:
        from ..utils import MAPPING_FILE
        from .led import FocusLED as Led
        from .locking import FocusLocking as Lock
        from .receptor import FocusReceptor as In
        from .socketcontrol import FocusSocketControl as Cout
        from .temperature import FocusTemperature as Temp
        from .voltage import FocusVoltage as Volt

        with shelve.open(MAPPING_FILE, 'n', protocol=4) as db:
            db['leds'] = Led
            db['lock'] = Lock
            db['ins'] = In
            db['couts'] = Cout
            db['temp'] = Temp
            db['volt'] = Volt

    @property
    def couts(self) -> dict:
        return self.complects['couts']

    @property
    def indicators(self) -> dict:
        return self.units['leds']

    @property
    def inputs(self) -> dict:
        return self.units['ins']

    @property
    def locking(self) -> Type[FocusLocking]:
        return self.units['lock']['lock']

    @property
    def temperature(self) -> dict:
        return self.units['temp']

    @property
    def voltage(self) -> Type[FocusVoltage]:
        return self.units['volt']['volt']
