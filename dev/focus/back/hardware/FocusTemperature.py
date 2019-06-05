import logging
from time import sleep

from gpiozero import CPUTemperature

from ..utils import Worker, get_sensor_file, log_and_report
from ..report import Reporter


class FocusTemperature(CPUTemperature):
    """Датчик температуры."""

    def __init__(self, **kwargs):
        self.ident = kwargs.pop('ident')
        self.description = kwargs.pop('description', None)

        super().__init__(sensor_file=self.sensor_file, **kwargs)

        self.hysteresis = kwargs.pop('hysteresis', 1.0)
        self.timedelta = kwargs.pop('timedelta', 60)

        self.logger = logging.getLogger('FP.%s' % __name__)
        self.logger.debug('Подготовка %s [%s]', self.ident, repr(self))

        self.reporter = Reporter(self.ident)

        self.service = Worker(self.state_monitor)

    @property
    def sensor_file(self):
        return get_sensor_file()

    @property
    def is_active(self):
        return self.hysteresis < abs(self.temperature - self.threshold)

    def state_monitor(self):
        """Контроль за порогом срабатывания."""

        self._tick = self.timedelta
        self.exceeded = False

        while True:
            sleep(1)
            self._tick -= 1

            if not self._tick:
                log_and_report(self, 'Текущая температура ',
                               self.temperature, msg_type='info')
                self._tick += self.timedelta

            if self.is_active and not self.exceeded:
                log_and_report(self, 'Перегрев ',
                               self.temperature, msg_type='warning')
                self.exceeded = True
            elif self.exceeded and not self.is_active:
                log_and_report(self, 'Норма ', self.temperature)
                self.exceeded = False
