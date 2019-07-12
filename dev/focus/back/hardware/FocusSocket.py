from .FocusLED import FocusLED
from ..utils.messaging_tools import log_and_report


class FocusSocket(FocusLED):
    """Гнездо (выходной разъём) со световым индикатором."""

    def __init__(self, **kwargs):
        super().__init__(initial_value=None, **kwargs)

    def on(self):
        "Включить гнездо."

        super().on()
        self.state = 1

        log_and_report(self, int(self.state))

    def off(self):
        "Отключить гнездо."

        super().off()
        self.state = 0

        log_and_report(self, int(self.state))

    def toggle(self):
        "Переключить гнездо."

        super().toggle()

        if self.state:
            self.state = 0
        else:
            self.state = 1

        log_and_report(self, int(self.state))
