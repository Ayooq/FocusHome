from . import FocusReceptor


class FocusVoltage(FocusReceptor):
    """Напряжение"""

    def __init__(self, **kwargs):
        kwargs.pop('postfix')
        super().__init__(postfix='', **kwargs)

    def on(self) -> None:
        super().on('info')

    def off(self) -> None:
        super().on('warning')
