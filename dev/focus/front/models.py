from flask_sqlalchemy import SQLAlchemy

from . import conn, device


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<Пользователь %r>' % self.username


class Focus(db.Model):
    __table__ = 'config'
    __mapper_args__ = {
        'include_properties': [
            'device_id',
            'device_name',
            'keepalive'
        ]
    }


class Temperature(db.Model):
    __table__ = 'config'
    __mapper_args__ = {
        'include_properties': [
            'cpu_min', 'cpu_max', 'cpu_threshold', 'cpu_delta',
            'board_min', 'board_max', 'board_threshold', 'board_delta',
        ]
    }


def _update_complects_state():
    for c in conn.complects.values():
        c.state


def _update_inputs_state():
    for i in conn.inputs.values():
        i.state


def _update_temperature_status():
    for t in conn.temperature.values():
        t.temperature


def update_values():
    _update_complects_state()
    _update_inputs_state()
    _update_temperature_status()


def get_data():
    update_values()

    data = {
        'device': device,
        'complects': conn.complects,
        'inputs': conn.inputs,
        'temperature': conn.temperature,
    }

    return data


def get_log():
    events = []

    with open('/home/pi/focus_pro/focus/focus.log') as log:
        for line in log:
            event = {}
            chunks = line.strip().split(' ')

            try:
                event['date'] = chunks[0]
                event['time'] = chunks[1]
                event['level'] = chunks[3]

                msg = ' '.join(chunks[4:])
                event['msg'] = msg
            except Exception:
                event['level'] = 'Плохой лог'
                event['msg'] = line

            events.append(event)

    events.reverse()

    data = {
        'device': device,
        'log': events,
    }

    return data
