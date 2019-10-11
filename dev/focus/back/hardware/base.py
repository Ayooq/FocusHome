import shelve
from typing import Type, Union

from gpiozero import Device

from ..feedback import Logger, Reporter
from ..utils.messaging import notify


class FocusBase(Device):
    """Базовый класс для любых компонентов устройства."""

    def __init__(self, **kwargs) -> None:
        self.id = kwargs.pop('id')
        self.description = self.__str__()

        self.logger = Logger.spawn_child(self.id)
        self.reporter = Reporter(self.id)

        super().__init__(**kwargs)

    def inform_state(self, **kwargs) -> None:
        notify(self, self.state, **kwargs)

    def _init_completed(self):
        notify(self, 'готово.', local_only=True)


class FocusBaseUnit(FocusBase):
    """Базовый класс для одиночных компонентов устройства.

    :param unit: класс инициируемого компонента
    :type unit: Device
    :param **kwargs: дополнительные именованные параметры
    :type **kwargs: dict
    """

    def __init__(self, unit: Type[Device], **kwargs) -> None:
        pin = kwargs.pop('pin', None)
        super().__init__(id=kwargs.pop('id'))

        if pin:
            self.unit = unit(pin, **kwargs)
        else:
            self.unit = unit(**kwargs)

    def __repr__(self) -> str:
        try:
            return f'id={self.id}, pin={self.unit.pin.number}'
        except AttributeError:
            return f'id={self.id}'

    @property
    def state(self) -> Union[int, bool, tuple]:
        return self.unit.value
