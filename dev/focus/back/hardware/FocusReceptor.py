from gpiozero import Button

from ..utils.messaging_tools import notify
from .FocusGPIO import FocusGPIO


class FocusReceptor(FocusGPIO):
    """Вход """

    def __init__(self, **kwargs):
        super().__init__(unit=Button, **kwargs)

        self.lock = False
        self.unit.when_pressed = self.on
        self.unit.when_released = self.off

    def on(self) -> None:
        if not self.lock:
            self.lock = True
            notify(self, 1)

    def off(self) -> None:
        if self.lock:
            self.lock = False
            notify(self, 0)

    @property
    def state(self) -> bool:
        return self.unit.is_pressed
