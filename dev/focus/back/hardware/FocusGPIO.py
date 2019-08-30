import logging

from gpiozero import DigitalInputDevice

from ..feedback.Reporter import Reporter


class FocusGPIO:
    """Базовый класс для устройств GPIO."""

    def __init__(self, unit=DigitalInputDevice, **kwargs):
        self.id = kwargs.pop('id')
        self.pin = kwargs.pop('pin')
        self.description = kwargs.pop(
            'descr', self.__doc__
        ) + kwargs.pop('postfix')

        self.unit = unit(self.pin, **kwargs)

        self.logger = logging.getLogger(__name__)
        msg_body = f'Подготовка {self.id}, {repr(self)}'
        self.logger.debug(msg_body)

        self.reporter = Reporter(self.id)

    def __repr__(self):
        return f'<id: {self.id}, pin: {self.pin}, descr: {self.description}>'
