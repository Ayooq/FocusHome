import logging

from . import Hardware
from .FocusSocket import FocusSocket
from .FocusReceptor import FocusReceptor
from ..logger import Logger
from ..reporting import Reporter


class FocusSocketControl:
    """Комплект [Гнездо — Контроль состояния]."""

    def __init__(self, **kwargs):
        self.id = kwargs.pop('id')
        self.description = kwargs.pop('description', None)

        out = kwargs.pop('out')
        out['id'] = self.id + '/out'

        cnt = kwargs.pop('cnt')
        cnt['id'] = self.id + '/cnt'

        self.socket = FocusSocket(**out)
        self.control = FocusReceptor(**cnt)

        self.logger = logging.getLogger('%s.%s' % (Hardware.prefix, __name__))
        self.logger.debug('Подготовка %s [%s]', self.id, repr(self))

        self.reporter = Reporter(self.id)

    def __repr__(self):
        return '%s (id=%r, description=%r)' % (
            self.__class__.__name__,
            self.id,
            self.description,
        )

    def on(self):
        """Включить контроль."""

        if self.socket.state:
            self.control.on()

    def off(self):
        """Отключить контроль."""

        if not self.socket.state:
            self.control.off()

    @property
    def state(self):
        return(self.socket.state, self.control.state)
