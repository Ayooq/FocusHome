from . import conn, device


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
