
from ..utils.messaging_tools import notify
from . import FocusLED


class FocusLocking(FocusLED):
    """Блокировка выходов"""

    def __init__(self, **kwargs):
        kwargs.pop('postfix')
        super().__init__(postfix='', **kwargs)
