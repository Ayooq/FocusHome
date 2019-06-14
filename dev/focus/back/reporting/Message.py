from .Content import Content


class Message(dict):
    """Сообщение для отчёта."""

    def __init__(self, mode):
        super().__init__()

        self.mode = mode
        self.setdefault(self.mode, Content())

    def _formalize(self, msg_type, msg_body, qos, retain):
        """Оформить содержимое в соответствии с указанным типом сообщения."""

        payload = self[self.mode]
        payload.inscribe(msg_type, msg_body, qos, retain)
