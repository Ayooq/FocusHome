import logging
from time import sleep

from gpiozero import CPUTemperature

from ..utils import Worker, get_sensor_file, log_and_report
from ..reporting import Reporter


class FocusTemperature(CPUTemperature):
    """Датчик температуры."""

    def __init__(self, **kwargs):
        self.ident = kwargs.pop('ident')
        self.description = kwargs.pop('description', None)

        super().__init__(sensor_file=self.sensor_file, **kwargs)

        self.hysteresis = kwargs.pop('hysteresis', 1.0)
        self.timedelta = kwargs.pop('timedelta', 60)

        self.logger = logging.getLogger('FocusPro.%s' % __name__)
        self.logger.debug('Подготовка %s [%s]', self.ident, repr(self))

        self.reporter = Reporter(self.ident)

        self.service = Worker(self.state_monitor)

    @property
    def sensor_file(self):
        return get_sensor_file()

    @property
    def is_active(self):
        return self.hysteresis < abs(self.temperature - self.threshold)

    @property
    def msg_body(self):
        return '%s °C' % self.temperature

    def state_monitor(self):
        """Следить за показателями температурных датчиков.

        Каждые :int self.timedelta: секунд сообщать информацию
        :attr msg_type='info': о текущем состоянии температуры внутри
        банкомата, а также ЦПУ самого устройства. При превышении порогового
        значения :float self.threshold:, с учётом показателя
        :float self.hysteresis:, предупреждать о перегреве
        :attr msg_type='warning': оборудования. В случае возвращения
        показателей в норму, отправлять соответствующее сообщение типа 'event'.
        """

        self._tick = self.timedelta
        self.exceeded = False

        while True:
            sleep(1)
            self._tick -= 1

            if not self._tick:
                log_and_report(self, self.msg_body, msg_type='info')
                self._tick += self.timedelta

            if self.is_active and not self.exceeded:
                log_and_report(self, self.msg_body, msg_type='warning')
                self.exceeded = True
            elif self.exceeded and not self.is_active:
                log_and_report(self, self.msg_body)
                self.exceeded = False
