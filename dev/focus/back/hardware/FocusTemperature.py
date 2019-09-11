import logging
from time import sleep
from typing import NoReturn

from gpiozero import CPUTemperature

from ..feedback import Reporter
from ..routines import Handler
from ..utils.messaging_tools import notify
from ..utils.one_wire import get_sensor_file


class FocusTemperature(CPUTemperature):
    """Датчик температуры """

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.description = self.__doc__
        self.description += 'ЦПУ' if self.id == 'cpu' else 'среды'

        sensor_file = get_sensor_file()
        self.__config = {
            'sensor_file': sensor_file,
            'min_temp': kwargs.get('min', 0.0),
            'max_temp': kwargs.get('max', 100.0),
            'threshold': kwargs.get('threshold', 80.0),
        }
        super().__init__(**self.__config)

        self.hysteresis = kwargs.get('hysteresis', 1.0)
        self.timedelta = kwargs.get('timedelta', 60)
        self.exceeded = False

        self.logger = logging.getLogger(__name__)
        msg_body = f'Подготовка {self.id}, {repr(self)}'
        self.logger.debug(msg_body)

        self.reporter = Reporter(self.id)

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

        await Handler.sleep_for(sec)
        notify(self, self.state, type_='info')

    async def watch_state(self) -> NoReturn:
        """Наблюдать за состоянием датчиков температуры.

        Информировать посредника о превышении установленного порога температуры
        (с учётом гистерезиса), а также оповещать посредника при возвращении
        показателей в норму.
        """

        if await self.is_exceeded():
            notify(self, self.state, type_='warning')
        else:
            notify(self, self.state)

    async def is_exceeded(self) -> None:
        if self.is_active and not self.exceeded:
            self.exceeded = True
        elif self.exceeded and not self.is_active:
            self.exceeded = False

    @property
    def is_active(self) -> bool:
        if super().is_active:
            self.hysteresis = -self.hysteresis

        return self.temperature + self.hysteresis > self.threshold

    @property
    def state(self) -> float:
        return self.temperature

    @state.setter
    def state(self, value) -> None:
        with open(self.sensor_file, 'w') as f:
            f.write(str(int(value * 1000)))
