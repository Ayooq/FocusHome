from datetime import datetime


class Address(dict):
    """Адресация сообщений."""

    def __init__(self, sender, receiver):
        super().__init__()

        self['from'] = sender
        self['to'] = receiver

        now = datetime.today()
        self['date'] = now.strftime('%Y%m%d%H%M%S')

    def get(self, report):
        return (report.get('from', 'system'), report.get('to', 'anymsg_body'))
