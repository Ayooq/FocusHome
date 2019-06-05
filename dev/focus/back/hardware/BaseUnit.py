import logging

from ..report import Reporter


class BaseUnit:
    """Базовый класс для устройств GPIO."""

    def __init__(self, unit=None, **kwargs):
        self.pin = kwargs.pop('pin')
        self.ident = kwargs.pop('ident')
        self.description = kwargs.pop('description', None)

        try:
            self.unit = unit(self.pin, **kwargs)
        except:
            print(
                'Компонент не установлен! Необходимо указать класс компонента библиотеки gpiozero.')
            raise

        self.logger = logging.getLogger('FP.%s' % __name__)
        self.logger.debug('Подготовка %s [%s]', self.ident, repr(self))

        self.reporter = Reporter(self.ident)

    def __repr__(self):
        return '%s (%r, pin=%r, id=%r, description=%r)' % (
            self.__class__.__name__,
            self.unit,
            self.pin,
            self.ident,
            self.description,
        )
