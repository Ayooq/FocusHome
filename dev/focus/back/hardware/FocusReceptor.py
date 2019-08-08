from gpiozero import Button

from ..utils.messaging_tools import log_and_report
from .FocusGPIO import FocusGPIO


class FocusReceptor(FocusGPIO):
    """Вход """

    def __init__(self, **kwargs):
        super().__init__(unit=Button, **kwargs)

        self.lock = False
        self.unit.when_pressed = self.on
        self.unit.when_released = self.off

    def on(self):
        if not self.lock:
            self.lock = True
            log_and_report(self, 1)

    def off(self):
        if self.lock:
            self.lock = False
            log_and_report(self, 0)

    @property
    def state(self):
        return self.unit.is_pressed
