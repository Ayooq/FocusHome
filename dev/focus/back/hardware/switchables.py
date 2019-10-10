from typing import Union

from gpiozero import DigitalOutputDevice

from .base import FocusBaseUnit


class FocusSwitchableUnit(FocusBaseUnit):
    """Класс одиночных компонентов, чьё состояние контролируется извне."""

    def __init__(self, **kwargs) -> None:
        unit = kwargs.pop('unit', DigitalOutputDevice)
        initial_value = kwargs.pop('initial_value', None)

        super().__init__(unit, initial_value=initial_value, **kwargs)

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
        self._postfix = kwargs['id'][-1]
        super().__init__(**kwargs)
        self._init_completed()

    def __str__(self):
        return f'Индикатор {self._postfix}'


class FocusSocketControl(FocusSwitchableUnit):
    """Класс компонентов, контролирующих состояние входных/выходных разъёмов."""

    def __init__(self, **kwargs):
        self.source = kwargs.pop('src')
        self.source.unit.when_activated = self.inform_source_state
        self.source.unit.when_deactivated = self.inform_source_state

        self._postfix = kwargs['id'][-1]
        super().__init__(**kwargs)
        self._init_completed()

    def __str__(self) -> str:
        return f'Контроль {self._postfix}'

    def inform_source_state(self):
        if self.state:
            report_type = 'info' if self.source.state else 'warning'
            self.source.inform_state(report_type=report_type)

    def on(self, **kwargs) -> None:
        if not self.state:
            super().on()
            self.inform_state()
            self.inform_source_state()

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
        super().__init__(**kwargs)
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
