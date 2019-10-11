from typing import Type, Union

from gpiozero import DigitalOutputDevice

from .base import FocusBaseUnit


class FocusSwitchableUnit(FocusBaseUnit):
    r"""Класс одиночных компонентов, чьё состояние контролируется извне.

    :param unit: класс инициируемого компонента, по умолчанию
    DigitalOutputDevice
    :type unit: gpiozero.Device, опционально
    :param **kwargs: дополнительные именованные параметры
    :type **kwargs: dict
    """

    def __init__(
            self,
            unit: Type[FocusBaseUnit] = DigitalOutputDevice,
            **kwargs,
    ) -> None:
        super().__init__(unit, **kwargs)

    def blink(self, *args, **kwargs) -> None:
        self.unit.blink(*args, **kwargs)

    def on(self, **kwargs) -> None:
        self.unit.on()

    def off(self, **kwargs) -> None:
        self.unit.off()

    def toggle(self, **kwargs) -> None:
        self.state = int(not self.value)

    @property
    def state(self) -> Union[int, float, str]:
        return super().state

    @state.setter
    def state(self, value: Union[int, str]) -> None:
        value = str(value).lower()

        if value in ('1', 'on', 'enable') or value.startswith('вкл'):
            self.on()
        elif value in ('0', 'off', 'disable') or value.startswith('выкл'):
            self.off()


class FocusLEDIndicator(FocusSwitchableUnit):
    """Класс световых индикаторов."""

    def __init__(self, **kwargs):
        active_high = kwargs.pop('active_high', False)
        initial_value = kwargs.pop('initial_value', False)
        self._postfix = kwargs['id'][-1]
        super().__init__(
            active_high=active_high, initial_value=initial_value, **kwargs)

        self._init_completed()

    def __str__(self):
        return f'Индикатор {self._postfix}'


class FocusSocket(FocusSwitchableUnit):
    """Класс входных/выходных разъёмов."""

    def __init__(self, **kwargs):
        self.control = kwargs.pop('src')
        self.control.unit.when_activated = self.control_on
        self.control.unit.when_deactivated = self.control_off

        active_high = kwargs.pop('active_high', True)
        initial_value = kwargs.pop('initial_value', None)
        self._postfix = kwargs['id'][-1]
        super().__init__(
            active_high=active_high, initial_value=initial_value, **kwargs)

        self._init_completed()

    def __str__(self) -> str:
        return f'Socket {self._postfix}'
    
    def __repr__(self) -> str:
        repr_ = super().__repr__()

        return f'{repr_}, src={self.control} <{repr(self.control)}>'
        
    def control_on(self):
        self.control.inform_state(report_type='info')

    def control_off(self):
        if self.state:
            self.control.inform_state(report_type='warning')

    def on(self, **kwargs) -> None:
        if not self.state:
            super().on()
            self.inform_state()

    def off(self, **kwargs) -> None:
        if self.state:
            super().off()
            self.inform_state()

    def toggle(self, **kwargs) -> None:
        if self.state:
            self.off()
        else:
            self.on()


class FocusSocketLockingSingleton(FocusSwitchableUnit):
    """Класс уникального компонента блокировки состояния выходов."""

    def __init__(self, **kwargs) -> None:
        active_high = kwargs.pop('active_high', True)
        initial_value = kwargs.pop('initial_value', None)
        super().__init__(
            active_high=active_high, initial_value=initial_value, **kwargs)

        self._init_completed()

    def __str__(self):
        return 'Блокировка состояния выходов'

    def on(self) -> None:
        if not self.state:
            super().on()
            self.inform_state()

    def off(self) -> None:
        if self.state:
            super().off()
            self.inform_state()

    def toggle(self) -> None:
        super().toggle()
        self.inform_state()
