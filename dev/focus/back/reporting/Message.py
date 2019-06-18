from .Content import Content


class Message(dict):
    """Сообщение для отчёта."""

    def __init__(self, mode: str):
        super().__init__()

        self.mode = mode
        self.setdefault(self.mode, Content())

    def _formalize(self, content: tuple):
        """Оформить содержимое в соответствии с указанным типом сообщения.

        Параметры:
          :param content: — кортеж из элементов, определяющих наполнение отчёта.
        """

        payload = self[self.mode]
        payload.inscribe(content)
