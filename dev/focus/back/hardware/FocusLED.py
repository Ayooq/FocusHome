from gpiozero import LED

from .BaseUnit import BaseUnit


class FocusLED(BaseUnit):
    """Световой индикатор.

    Без логирования и публикации.
    """

    def __init__(self, **kwargs):
        super().__init__(unit=LED, **kwargs)

    @property
    def state(self):
        return self.unit.is_lit

    def set_state(self, value):
        if value in ('ON', 'on', 'Вкл', 'вкл', 'Включить', 'включить', 1):
            self.on()
        else:
            self.off()

    def blink(self, *args, **kwargs):
        self.unit.blink(*args, **kwargs)

    def on(self):
        """Зажечь индикатор."""

        self.unit.on()

    def off(self):
        """Погасить индикатор."""

        self.unit.off()

    def toggle(self):
        """Изменить состояние индикатора."""

        self.unit.toggle()
