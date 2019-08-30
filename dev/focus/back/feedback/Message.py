from .Content import Content


class Message(dict):
    """Сообщение для отчёта."""

    def __init__(self, topic: str):
        super().__init__()

        self.topic = topic
        self.setdefault(self.topic, Content())

    def _formalize(self, content: tuple):
        """Оформить содержимое в соответствии с указанным типом сообщения.

        Параметры:
          :param content: — кортеж из элементов, определяющих наполнение отчёта.
        """

        report = self[self.topic]
        report.inscribe(content)
