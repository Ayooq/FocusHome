import logging
from time import sleep

from gpiozero import CPUTemperature

from ..reporting import Reporter
from ..utils.one_wire import get_sensor_file
from ..utils.concurrency import Worker
from ..utils.messaging_tools import log_and_report


class FocusTemperature(CPUTemperature):
    """Датчик температуры """

    def __init__(self, **kwargs):
        self.id = kwargs.pop('id')
        self.description = self.__doc__
        self.description += 'ЦПУ' if self.id == 'cpu' else 'среды'

        self.__config = {
            'sensor_file': get_sensor_file(),
            'min_temp': kwargs.pop('min'),
            'max_temp': kwargs.pop('max'),
            'threshold': kwargs.pop('threshold'),
        }
        super().__init__(**self.__config)

        self.hysteresis = kwargs.pop('hysteresis', 1.0)
        self.timedelta = kwargs.pop('timedelta', 60)

        self.logger = logging.getLogger(__name__)
        self.logger.debug('Подготовка %s [%s]', self.id, repr(self))

        self.reporter = Reporter(self.id)

        self.service = Worker(self.state_monitor)

    def state_monitor(self):
        """Отслеживание изменений показателей температурных датчиков.

        Каждые :int self.timedelta: секунд сообщать информацию
        :attr type_="info": о текущем состоянии температуры внутри
        банкомата, а также ЦПУ самого устройства. При превышении порогового
        значения :float self.threshold:, с учётом показателя
        :float self.hysteresis:, предупреждать о перегреве
        :attr type_="warning": оборудования. В случае возвращения
        показателей в норму, отправлять соответствующее сообщение типа "event".
        """

        self._tick = self.timedelta
        self._exceeded = False

        while True:
            sleep(1)
            self._tick -= 1

            if not self._tick:
                log_and_report(self, self.state, type_='info')
                self._tick += self.timedelta

            if self.is_active and not self._exceeded:
                log_and_report(self, self.state, type_='warning')
                self._exceeded = True
            elif self._exceeded and not self.is_active:
                log_and_report(self, self.state)
                self._exceeded = False

    @property
    def state(self):
        return self.temperature

    @property
    def is_active(self):
        if super().is_active:
            self.hysteresis = -self.hysteresis

        return self.temperature + self.hysteresis > self.threshold
