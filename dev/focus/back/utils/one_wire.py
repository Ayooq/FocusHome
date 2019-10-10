"""Модуль для работы с устройствами, реализующими протокол 1-Wire.

Функции:
    :func get_sensor_file(): — вернуть абсолютный путь к файлу, содержащему
текущий показатель датчика температуры.
"""
import glob


def get_sensor_file() -> str:
    """Вернуть абсолютный путь к файлу, содержащему текущий показатель датчика
    температуры."""
    try:
        sensor_file = glob.glob(
            '/sys/bus/w1/devices/28*/hwmon/hwmon0/temp1_input'
        )[0]
    except IndexError:
        sensor_file = '/sys/class/thermal/thermal_zone0/temp'

    return sensor_file
