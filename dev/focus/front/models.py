from . import focus
from focus.back.utils import LOG_FILE


def update_values():
    _get_inputs_status()
    _get_complects_status()
    _get_temperature_status()
    _get_miscellaneous_status()


def _get_inputs_status():
    for _ in focus.inputs.values():
        _.state


def _get_complects_status():
    for _ in focus.complects.values():
        _.socket.state
        _.control.state


def _get_temperature_status():
    for _ in focus.temperature.values():
        _.temperature


def _get_miscellaneous_status():
    for _ in focus.misc.values():
        _.state


def get_data():
    update_values()

    data = {
        'device': focus,
        'inputs': focus.inputs,
        'complects': focus.complects,
        'temperature': focus.temperature,
        'misc': focus.misc,
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
        'device': focus,
        'log': events,
    }

    return data
