from gpiozero import LED

from .BaseUnit import BaseUnit


class FocusLED(BaseUnit):
    """Световой индикатор.

    Без логирования и публикации.
    """

    def __init__(self, **kwargs):
        super().__init__(unit=LED, **kwargs)

    def on(self):
        """Зажечь индикатор."""

        self.unit.on()

    def off(self):
        """Погасить индикатор."""

        self.unit.off()

    def toggle(self):
        """Изменить состояние индикатора на противоположное."""

        self.unit.toggle()

    def blink(self, *args, **kwargs):
        """Прокси для метода моргания у класса LED."""

        self.unit.blink(*args, **kwargs)

    @property
    def state(self):
        return self.unit.is_lit

    @state.setter
    def state(self, value):
        if value == 1 or str(value).lower() in ('on', 'вкл', 'включить'):
            self.on()
        elif value == 0 or str(value).lower() in ('off', 'выкл', 'выключить'):
            self.off()
