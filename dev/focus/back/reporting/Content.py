class Content(dict):
    """Структура содержимого для сообщений."""

    def __init__(self):
        super().__init__()

        for key in Content.keys:
            self.setdefault(key)

    def inscribe(self, msg_type, msg_body, qos, retain):
        """Вписать содержимое."""

        self['msg_type'] = msg_type
        self['msg_body'] = msg_body
        self['qos'] = qos
        self['retain'] = retain

    keys = (
        'msg_type',
        'msg_body',
        'qos',
        'retain',
    )
