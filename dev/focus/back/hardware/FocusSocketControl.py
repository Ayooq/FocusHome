import logging

from ..reporting import Reporter
from ..utils.messaging_tools import log_and_report
from .FocusReceptor import FocusReceptor
from .FocusSocket import FocusSocket


class FocusSocketControl:
    """Комплект [Выход — Контроль] """

    def __init__(self, **kwargs):
        self.id = kwargs.pop('id')
        postfix = kwargs.pop('postfix')
        self.description = self.__doc__ + postfix

        complect = [(id_, gpio) for id_, gpio in kwargs.items()]

        out = max(complect)
        out_id = out[0] + postfix

        cnt = min(complect)
        cnt_id = cnt[0] + postfix

        print(out_id, out, cnt_id, cnt)

        self.socket = FocusSocket(id=out_id, postfix=postfix, **out[1])
        print(self.socket)
        self.control = FocusReceptor(
            id=cnt_id, descr='Контроль ', postfix=postfix, **cnt[1]
        )
        print(self.control)
        self.logger = logging.getLogger(__name__)
        self.logger.debug('Подготовка %s [%s]', self.id, repr(self))

        self.reporter = Reporter(self.id)
        self.control.reporter = Reporter(self.control.id)

    def __repr__(self):
        return '%s (id=%r, units=[%r, %r], description=%r)' % (
            self.__class__.__name__,
            self.id,
            self.socket,
            self.control,
            self.description,
        )

    def on(self):
        self.control.on()
        self.socket.on()

        log_and_report(self.control, int(self.socket.state))

    def off(self):
        self.control.off()
        self.socket.off()

        log_and_report(self.control, int(self.socket.state))

    def toggle(self):
        self.control.lock = False if self.control.lock else True
        self.socket.toggle()

        log_and_report(self.control, int(self.socket.state))
