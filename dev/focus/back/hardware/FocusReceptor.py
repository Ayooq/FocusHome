from gpiozero import Button

from .BaseUnit import BaseUnit
from ..utils.messaging_tools import log_and_report


class FocusReceptor(BaseUnit):
    """Концевой датчик (входной рецептор)."""

    def __init__(self, **kwargs):
        super().__init__(unit=Button, **kwargs)

        self.lock = True
        self.unit.when_pressed = self.on
        self.unit.when_released = self.off

    def on(self):
        """Замкнуть цепь на приём сигнала."""

        if not self.lock:
            self.lock = True
            log_and_report(self, 'включён')

    def off(self):
        """Разомкнуть цепь подачи сигнала."""

        if self.lock:
            self.lock = False
            log_and_report(self, 'отключён')

    @property
    def state(self):
        return self.unit.value
