from gpiozero import LED

from .FocusGPIO import FocusGPIO


class FocusLED(FocusGPIO):
    """Световой индикатор """

    def __init__(self, **kwargs):
        super().__init__(unit=LED, **kwargs)

    def on(self) -> None:
        self.unit.on()

    def off(self) -> None:
        self.unit.off()

    def toggle(self) -> None:
        self.unit.toggle()

    def blink(self, *args, **kwargs) -> None:
        """Прокси для метода моргания у класса LED."""

        self.unit.blink(*args, **kwargs)

    @property
    def state(self) -> bool:
        return self.unit.is_lit

    @state.setter
    def state(self, value) -> None:
        if value == 1 or str(value).lower() in ('on', 'вкл', 'включить'):
            self.on()
        elif value == 0 or str(value).lower() in ('off', 'выкл', 'выключить'):
            self.off()
