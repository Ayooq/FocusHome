class Content(dict):
    """Структура содержимого для сообщений."""

    _subkeys = (
        'msg_type',
        'msg_body',
    )

    def __init__(self):
        super().__init__()

        for key in Content._subkeys:
            self.setdefault(key)

    def inscribe(self, msg_type, msg_body):
        """Вписать содержимое."""

        self['msg_type'] = msg_type
        self['msg_body'] = msg_body
