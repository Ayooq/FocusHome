import glob


def get_sensor_file():
    return glob.glob('/sys/bus/w1/devices/28*/hwmon/hwmon0/temp1_input')
