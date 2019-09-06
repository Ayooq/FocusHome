from ..utils.messaging_tools import notify
from .FocusGPIO import FocusGPIO


class FocusVoltage(FocusGPIO):
    """Напряжение"""

    def __init__(self, **kwargs):
        kwargs.pop('postfix')
        super().__init__(postfix='', **kwargs)

        self.unit.when_activated = self.on
        self.unit.when_deactivated = self.off

    def on(self) -> None:
        notify(self, 1)

    def off(self) -> None:
        notify(self, 0, type_='warning')

    @property
    def state(self) -> bool:
        return self.unit.is_active
