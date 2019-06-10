import logging

from .FocusSocket import FocusSocket
from .FocusReceptor import FocusReceptor
from ..reporting import Reporter


class FocusSocketControl:
    """Комплект [Гнездо — Контроль состояния]."""

    def __init__(self, **kwargs):
        self.ident = kwargs.pop('ident')
        self.description = kwargs.pop(
            'description', 'Комплект %s' % self.ident[-1])

        kout = kwargs.pop('out')
        kout['ident'] = self.ident + '/out'

        kcnt = kwargs.pop('cnt')
        kcnt['ident'] = self.ident + '/cnt'

        self.socket = FocusSocket(**kout)
        self.control = FocusReceptor(**kcnt)

        self.logger = logging.getLogger('FocusPro.%s' % __name__)
        self.logger.debug('Подготовка %s [%s]', self.ident, repr(self))

        self.reporter = Reporter(self.ident)

    def __repr__(self):
        return '%s (id=%r, description=%r)' % (
            self.__class__.__name__,
            self.ident,
            self.description,
        )

    def on(self):
        """Включить гнездо."""

        if not self.control.lock and not self.socket.state:
            self.control.lock = True
            self.socket.on()

    def off(self):
        """Отключить гнездо."""

        if self.control.lock and self.socket.state:
            self.control.lock = False
            self.socket.off()

    @property
    def state(self):
        return(self.socket.state, self.control.state)
