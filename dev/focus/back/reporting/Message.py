from .Content import Content


class Message(dict):
    """Сообщение для отчёта, оформленное в соответствии с указанным типом."""

    def __init__(self, mode):
        super().__init__()
        self._content = mode
        self.setdefault(mode, Content())

    def _formalize(self, msg_type, msg_body):
        """Официально оформить содержимое."""

        payload = self[self._content]
        payload.inscribe(msg_type, msg_body)
