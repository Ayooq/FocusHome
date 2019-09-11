from gpiozero import Button

from ..utils.messaging_tools import notify
from . import FocusGPIO


class FocusReceptor(FocusGPIO):
    """Вход """

    def __init__(self, **kwargs):
        super().__init__(unit=Button, **kwargs)

        self.lock = False
        self.unit.when_pressed = self.on
        self.unit.when_released = self.off

    def on(self, msg_type='event') -> None:
        if not self.lock:
            self.lock = True
            notify(self, 1, type_=msg_type)

    def off(self, msg_type='event') -> None:
        if self.lock:
            self.lock = False
            notify(self, 0, type_=msg_type)

    @property
    def state(self) -> bool:
        return self.unit.is_pressed
