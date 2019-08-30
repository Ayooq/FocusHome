class Content(dict):
    """Структура содержимого для сообщений."""

    _mapping = (
        'from',
        'type',
        'message',
        'qos',
        'retain',
    )

    def __init__(self):
        super().__init__()

        for key in Content._mapping:
            self.setdefault(key)

    def inscribe(self, values: tuple):
        """Вписать содержимое в словарь отчёта.

        Параметры:
          :param values: — кортеж из элементов, определяющих наполнение отчёта.
        """

        data = zip(Content._mapping, values)
        self.update(data)
