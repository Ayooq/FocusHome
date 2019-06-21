import glob


def get_sensor_file():
    """Вернуть абсолютный путь к файлу текущего показателя температуры."""

    return glob.glob('/sys/bus/w1/devices/28*/hwmon/hwmon0/temp1_input')[0]
