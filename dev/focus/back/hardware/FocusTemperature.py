import logging
from time import sleep
from typing import NoReturn

from gpiozero import CPUTemperature

from ..feedback.Reporter import Reporter
from ..utils.concurrency import sleep_for
from ..utils.messaging_tools import notify
from ..utils.one_wire import get_sensor_file


class FocusTemperature(CPUTemperature):
    """Датчик температуры """

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.description = self.__doc__
        self.description += 'ЦПУ' if self.id == 'cpu' else 'среды'

        self.__config = {
            'sensor_file': get_sensor_file(),
            'min_temp': kwargs.get('min', 0.0),
            'max_temp': kwargs.get('max', 100.0),
            'threshold': kwargs.get('threshold', 80.0),
        }
        super().__init__(**self.__config)

        self.hysteresis = kwargs.get('hysteresis', 1.0)
        self.timedelta = kwargs.get('timedelta', 60)

        self.logger = logging.getLogger(__name__)
        msg_body = f'Подготовка {self.id}, {repr(self)}'
        self.logger.debug(msg_body)

        self.reporter = Reporter(self.id)

        self.exceeded = False

    def __repr__(self):
        return f'<id: {self.id}, descr: {self.description}>'

    async def report_at_intervals(self, sec: int) -> NoReturn:
        """Отслеживать изменения показателей температурных датчиков c заданной
        периодичностью.

        Логировать и отсылать посреднику информацию о текущей температуре
        датчиков каждые :attr sec: секунд.

        Параметры:
          :param sec: — интервал в секундах, устанавливающий периодичность
        оповещений, формируемых компонентом.
        """

        await sleep_for(sec)
        notify(self, self.state, type_='info')

    async def watch_state(self) -> NoReturn:
        """Наблюдать за состоянием датчиков температуры.

        Информировать посредника о превышении установленного порога температуры
        (с учётом гистерезиса), а также оповещать посредника при возвращении
        показателей в норму.
        """

        if self.is_active and not self.exceeded:
            notify(self, self.state, type_='warning')
            self.exceeded = True
        elif self.exceeded and not self.is_active:
            notify(self, self.state)
            self.exceeded = False

    @property
    def state(self) -> float:
        return self.temperature

    @property
    def is_active(self) -> bool:
        if super().is_active:
            self.hysteresis = -self.hysteresis

        return self.temperature + self.hysteresis > self.threshold
