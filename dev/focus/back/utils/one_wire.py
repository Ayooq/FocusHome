import glob


def get_sensor_file() -> str:
    """Вернуть абсолютный путь к файлу текущего показателя температуры."""

    try:
        sensor_file = glob.glob(
            '/sys/bus/w1/devices/28*/hwmon/hwmon0/temp1_input'
        )[0]
    except IndexError:
        sensor_file = '/sys/class/thermal/thermal_zone0/temp'

    return sensor_file
