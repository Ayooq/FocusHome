from ..utils.messaging_tools import log_and_report
from .FocusLED import FocusLED


class FocusSocket(FocusLED):
    """Выход """

    def __init__(self, **kwargs):
        super().__init__(initial_value=None, **kwargs)
