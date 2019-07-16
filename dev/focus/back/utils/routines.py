import os

from .messaging_tools import log_and_report


def on_event(self, event, changed_unit, target_unit, time_limit=0):
    current_state = changed_unit.state
    
    while time_limit:
        if changed_unit.state != current_state:
            return

        time_limit -= 1

    os.system('sudo reboot') if event == 'reload' else target_unit.toggle()

    return target_unit.state
