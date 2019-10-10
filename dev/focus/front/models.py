from focus.back.utils import LOG_FILE

from . import focus_pro


def update_values():
    for group_families in focus_pro.hardware.values():
        for family_components in group_families.values():
            [component.state for component in family_components.values()]


def get_data():
    update_values()

    data = {
        'device': focus_pro,
        'control': (
            cmp for uid, cmp in focus_pro.couts.items() if uid.startswith('cnt')
        ),
        'inputs': focus_pro.inputs,
        'locking': focus_pro.locking,
        'temperature': focus_pro.temperature,
        'voltage': focus_pro.voltage,
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
