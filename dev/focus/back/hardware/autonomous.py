from typing import Type, Union

from gpiozero import CPUTemperature, DigitalInputDevice

from ..utils.one_wire import get_sensor_file
from .base import FocusBaseUnit


class FocusAutonomousUnit(FocusBaseUnit):
    r"""Класс одиночных компонентов, способных управлять своим состоянием.

    :param unit: класс инициируемого компонента, по умолчанию
    DigitalOutputDevice
    :type unit: gpiozero.Device, опционально
    :param **kwargs: дополнительные именованные параметры
    :type **kwargs: dict
    """

    def __init__(
            self,
            unit: Type[FocusBaseUnit] = DigitalInputDevice,
            **kwargs,
    ) -> None:
        super().__init__(unit, **kwargs)

        self.unit.when_activated = self.inform_state
        self.unit.when_deactivated = self.inform_state


class FocusExternalReceptor(FocusAutonomousUnit):
    """Класс рецепторов внешнего воздействия."""

    def __init__(self, **kwargs):
        self._postfix = kwargs['id'][-1]
        pull_up = kwargs.pop('pull_up', True)
        # bounce_time = kwargs.pop('bounce_time', 0.1)
        super().__init__(
            pull_up=pull_up,
            # bounce_time=bounce_time,
            **kwargs
        )

        self._init_completed()

    def __str__(self):
        return f'Вход {self._postfix}'


class FocusSocketControl(FocusAutonomousUnit):
    """Класс компонентов, контролирующих состояние входных/выходных разъёмов."""

    def __init__(self, **kwargs):
        self._postfix = kwargs['id'][-1]
        pull_up = kwargs.pop('pull_up', True)
        # active_state = kwargs.pop('active_state', False)
        bounce_time = kwargs.pop('bounce_time', 1.0)
        super().__init__(
            pull_up=pull_up,
            # active_state=active_state,
            bounce_time=bounce_time,
            **kwargs,
        )

        self._init_completed()

    def __str__(self):
        return f'Control {self._postfix}'


class FocusTemperatureSensor(FocusAutonomousUnit):
    """Класс температурных датчиков."""

    def __init__(self, **kwargs) -> None:
        self._postfix = 'ЦПУ' if kwargs['id'][-1] == 'u' else 'среды'
        sensor_file = get_sensor_file()
        kwargs.update({
            'sensor_file': sensor_file,
            'min_temp': kwargs.get('min', 0.0),
            'max_temp': kwargs.get('max', 100.0),
            'threshold': kwargs.get('threshold', 80.0),
        })
        super().__init__(unit=CPUTemperature, **kwargs)

        self.hysteresis = kwargs.get('hysteresis', 1.0)
        self.timedelta = kwargs.get('timedelta', 60)

        self._init_completed()

    def __str__(self) -> str:
        return f'Датчик температуры {self._postfix}'

    @property
    def is_active(self) -> bool:
        if super().is_active:
            self.hysteresis = -self.hysteresis

        return self.unit.temperature + self.hysteresis > self.threshold

    @property
    def state(self) -> float:
        return self.unit.temperature

    @state.setter
    def state(self, value: Union[str, float]) -> None:
        with open(self.sensor_file, 'w') as f:
            f.write(str(1000 * float(value)))


class FocusVoltageControlSingleton(FocusAutonomousUnit):
    """Класс уникального компонента контроля напряжения в сети."""

    def __init__(self, **kwargs) -> None:
        pull_up = kwargs.pop('pull_up', False)
        bounce_time = kwargs.pop('bounce_time', 1.0)
        super().__init__(pull_up=pull_up, bounce_time=bounce_time, **kwargs)

        self.unit.when_activated = self.on
        self.unit.when_deactivated = self.off

        self._init_completed()

    def on(self) -> None:
        self.inform_state('info')

    def off(self) -> None:
        self.inform_state('warning')

    def __str__(self):
        return 'Состояние электропитания устройства'
