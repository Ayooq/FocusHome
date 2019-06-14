class Address(dict):
    """Адресация сообщений."""

    def __init__(self, sender, receiver):
        super().__init__()

        self['from'] = sender
        self['to'] = receiver

    def get(self, report):
        return (report.get('from', 'system'), report.get('to', 'anybody'))
