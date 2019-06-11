from .FocusLED import FocusLED
from ..utils.messaging_tools import log_and_report


class FocusSocket(FocusLED):
    """Гнездо (выходной разъём) со световым индикатором."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on(self):
        "Включить гнездо."

        super().on()
        log_and_report(self, 'включено.')

    def off(self):
        "Отключить гнездо."

        super().off()
        log_and_report(self, 'отключено.')

    def toggle(self):
        "Переключить гнездо."

        super().toggle()
        log_and_report(self, 'переключено.')
