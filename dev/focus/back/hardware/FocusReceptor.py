from gpiozero import Button

from .BaseUnit import BaseUnit
from ..utils.messaging_tools import log_and_report


class FocusReceptor(BaseUnit):
    """Концевой датчик (входной рецептор)."""

    def __init__(self, external_callbacks=False, **kwargs):
        super().__init__(unit=Button, **kwargs)
        self.lock = True

        if not external_callbacks:
            self.add_callbacks(self.on, self.off)

    def add_callbacks(self, func1, func2):
        self.unit.when_pressed = func1
        self.unit.when_released = func2

    def on(self):
        """Замкнуть цепь на приём сигнала."""

        if not self.lock and self.state:
            self.lock = True

            log_and_report(self, 'включён')

    def off(self):
        """Разомкнуть цепь подачи сигнала."""

        if self.lock and not self.state:
            self.lock = False

            log_and_report(self, 'отключён')

    @property
    def state(self):
        return self.unit.is_pressed
