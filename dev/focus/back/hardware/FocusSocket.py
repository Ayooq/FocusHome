from .FocusLED import FocusLED
from ..utils.messaging_tools import log_and_report


class FocusSocket(FocusLED):
    """Выход """

    def __init__(self, **kwargs):
        super().__init__(initial_value=None, **kwargs)
