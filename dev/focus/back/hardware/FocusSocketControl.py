import logging

from .FocusSocket import FocusSocket
from .FocusReceptor import FocusReceptor
from ..reporting import Reporter
from ..utils.messaging_tools import log_and_report


class FocusSocketControl:
    """Комплект [Выход — Контроль] """

    def __init__(self, **kwargs):
        self.id = kwargs.pop('id')
        postfix = kwargs.pop('postfix')
        self.description = self.__doc__ + postfix
        self.complect = []

        for id_, unit in kwargs.items():
            unit['id'] = id_
            self.complect.append(unit)

        self.socket = FocusSocket(postfix=postfix, **self.complect[0])
        self.control = FocusReceptor(
            descr='Контроль ', postfix=postfix, **self.complect[1]
        )

        self.logger = logging.getLogger(__name__)
        self.logger.debug('Подготовка %s [%s]', self.id, repr(self))

        self.reporter = Reporter(self.id)

    def __repr__(self):
        return '%s (id=%r, description=%r)' % (
            self.__class__.__name__,
            self.id,
            self.description,
        )

    def on(self):
        self.control.on()
        self.socket.on()

    def off(self):
        self.control.off()
        self.socket.off()

    def toggle(self):
        self.control.lock = False if self.control.lock else True
        self.socket.toggle()

        log_and_report(self.control, int(self.socket.state))
