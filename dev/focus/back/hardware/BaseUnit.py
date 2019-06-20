import logging

from gpiozero import DigitalInputDevice

from ..reporting import Reporter


class BaseUnit:
    """Базовый класс для устройств GPIO."""

    def __init__(self, unit=DigitalInputDevice, **kwargs):
        self.id = kwargs.pop('id')
        self.pin = kwargs.pop('pin')
        self.description = kwargs.pop('description', None)
        self.unit = unit(self.pin, **kwargs)

        self.logger = logging.getLogger(__name__)
        self.logger.debug('Подготовка %s [%s]', self.id, repr(self))

        self.reporter = Reporter(self.id)

    def __repr__(self):
        return '%s (id=%r, pin=%r, unit=%r, description=%r)' % (
            self.__class__.__name__,
            self.id,
            self.pin,
            self.unit,
            self.description,
        )
