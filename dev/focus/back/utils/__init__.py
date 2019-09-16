import os

ROOT_DIR = os.path.abspath(os.path.curdir)
MAPPING_DIR = f'{ROOT_DIR}/back/hardware'
ROUTINES_DIR = f'{ROOT_DIR}/back/commands'

FILENAMES = 'config', 'focus'

MAPPING_FILE = f'{MAPPING_DIR}/map'
ROUTINES_FILE = f'{ROUTINES_DIR}/routines'

CONFIG_FILE = f'{ROOT_DIR}/{FILENAMES[0]}.yml'
BACKUP_FILE = f'{ROOT_DIR}/{FILENAMES[0]}.bak'

LOG_FILE = f'{ROOT_DIR}/{FILENAMES[1]}.log'
DB_FILE = os.getenv('DB_LOCAL', f'{FILENAMES[1]}.db')
