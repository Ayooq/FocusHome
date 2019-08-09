from focus.back.utils import LOG_FILE

from . import focus_pro


def update_values():
    _get_couts_status()
    _get_inputs_status()
    _get_temperature_status()
    _get_miscellaneous_status()


def _get_couts_status():
    for _ in focus_pro.couts.values():
        _.socket.state
        _.control.state


def _get_inputs_status():
    for _ in focus_pro.inputs.values():
        _.state


def _get_temperature_status():
    for _ in focus_pro.temperature.values():
        _.temperature


def _get_miscellaneous_status():
    for _ in focus_pro.misc.values():
        _.state


def get_data():
    update_values()

    data = {
        'device': focus_pro,
        'inputs': focus_pro.inputs,
        'complects': focus_pro.couts,
        'temperature': focus_pro.temperature,
        'misc': focus_pro.misc,
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
        'device': focus_pro,
        'log': events,
    }

    return data
