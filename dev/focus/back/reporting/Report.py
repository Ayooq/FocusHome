from .Message import Message


class Report(Message):
    """Отчёт на основе сообщения по указанному типу."""

    def __init__(self, msg_type=None, msg_body=None, mode='report'):
        super().__init__(mode)

    def event(self, msg_body):
        self._formalize('event', msg_body)
        return self

    def info(self, msg_body):
        self._formalize('info', msg_body)
        return self

    def warning(self, msg_body):
        self._formalize('warning', msg_body)
        return self

    def error(self, msg_body):
        self._formalize('error', msg_body)
        return self

    def set_type(self, msg_type, msg_body):
        self._formalize(msg_type, msg_body)
        return self
