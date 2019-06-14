from . import c, device
from focus.back.utils import LOG_FILE


def _get_complects_status():
    for _ in c.complects.values():
        _.state


def _get_inputs_status():
    for _ in c.inputs.values():
        _.state


def _get_temperature_status():
    for _ in c.temperature.values():
        _.temperature


def update_values():
    _get_complects_status()
    _get_inputs_status()
    _get_temperature_status()


def get_data():
    update_values()

    data = {
        'device': device,
        'complects': c.complects,
        'inputs': c.inputs,
        'temperature': c.temperature,
    }

    return data


def get_log():
    events = []

    with open(LOG_FILE) as log:
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
