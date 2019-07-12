import os

from .messaging_tools import log_and_report


def on_voltage_failure(voltage, battery_unit, time_limit=0):
    while time_limit:
        if voltage.state:
            return

        time_limit -= 1

    battery_unit.on()

    return True


def on_voltage_recovery(battery_unit):
    battery_unit.off()


def on_overheat(sensor, cooler, time_limit=0):
    while time_limit:
        if not sensor.is_active:
            return

        time_limit -= 1

    cooler.on()


def on_cooldown(cooler):
    cooler.off()


def on_state_change(changed_unit, target_unit, time_limit=0, reload=False):
    current_state = changed_unit.state

    while time_limit:
        if changed_unit.state != current_state:
            return

        time_limit -= 1

    os.system('sudo reboot') if reload else target_unit.toggle()
