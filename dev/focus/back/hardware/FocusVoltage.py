from .BaseUnit import BaseUnit
from ..utils.db_handlers import fill_table
from ..utils.messaging_tools import log_and_report


class FocusVoltage(BaseUnit):
    """Напряжение"""

    def __init__(self, **kwargs):
        kwargs.pop('postfix')
        super().__init__(postfix='', **kwargs)

        self.unit.when_activated = self.on
        self.unit.when_deactivated = self.off

    def on(self):
        log_and_report(self, 1)

    def off(self):
        log_and_report(self, 0, type_='warning')

    @property
    def state(self):
        return self.unit.is_active
