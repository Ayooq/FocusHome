import logging

from ..feedback.Reporter import Reporter
from ..utils.messaging_tools import notify
from .FocusLED import FocusLED
from .FocusReceptor import FocusReceptor


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

        self.socket = FocusLED(
            id=out_id, postfix=postfix, initial_value=None, **out[1])
        self.control = FocusReceptor(
            id=cnt_id, descr='Контроль ', postfix=postfix, **cnt[1])

        self.logger = logging.getLogger(__name__)
        msg_body = f'Подготовка {self.id}, {repr(self)}'
        self.logger.debug(msg_body)

        self.reporter = Reporter(self.id)
        self.control.reporter = Reporter(self.control.id)

    def __repr__(self) -> str:
        return f'<id: {self.id}, descr: {self.description}>'

    def on(self) -> None:
        self.control.on()
        self.socket.on()

        notify(self.control, int(self.socket.state))

    def off(self) -> None:
        self.control.off()
        self.socket.off()

        notify(self.control, int(self.socket.state))

    def toggle(self) -> None:
        self.control.lock = False if self.control.lock else True
        self.socket.toggle()

        notify(self.control, int(self.socket.state))
