import os

ROOT_DIR = os.path.abspath(os.path.curdir)

COMMANDS_DIR = f'{ROOT_DIR}/back/commands'
HARDWARE_DIR = f'{ROOT_DIR}/back/hardware'

FILENAMES = 'config', 'focus', 'macros', 'mapping'

MACROS_FILE = f'{COMMANDS_DIR}/{FILENAMES[-2]}'
MAPPING_FILE = f'{HARDWARE_DIR}/{FILENAMES[3]}'

CONFIG_FILE = f'{ROOT_DIR}/{FILENAMES[0]}.yml'
BACKUP_FILE = f'{ROOT_DIR}/{FILENAMES[0]}.bak'

LOG_FILE = f'{ROOT_DIR}/{FILENAMES[1]}.log'
DB_FILE = os.getenv('DB_LOCAL', f'{FILENAMES[1]}.db')

SNMP_OIDS = ['1.3.6.1.2.1.1.5.0']
SNMP_COUNT = '1.3.6.1.2.1.2.1.0'
SNMP_START = 0
