from .BaseUnit import BaseUnit
from ..utils.db_handlers import fill_table
from ..utils.messaging_tools import log_and_report


class FocusVoltage(BaseUnit):
    """Контроль напряжения устройства."""

    def __init__(self):
        super().__init__()

        self.unit.when_activated = self.on
        self.unit.when_deactivated = self.off

    def on(self):
        """Напряжение подаётся."""

        log_and_report(self, 'в норме')

    def off(self):
        """Напряжение пропало."""

        log_and_report(self, 'не подаётся', msg_type='warning')

    @property
    def state(self):
        return self.unit.value
