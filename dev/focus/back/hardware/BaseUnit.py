import logging

from gpiozero import InternalDevice

from . import Hardware
from ..reporting import Reporter


class BaseUnit:
    """Базовый класс для устройств GPIO."""

    def __init__(self, unit=InternalDevice, **kwargs):
        self.id = kwargs.pop('id')
        self.pin = kwargs.pop('pin')
        self.unit = unit(self.pin, **kwargs)
        self.description = kwargs.pop('description', None)

        self.logger = logging.getLogger('%s.%s' % (Hardware.prefix, __name__))
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
