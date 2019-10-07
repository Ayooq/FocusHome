import os

# import socket as s

REDIS_HOST = 'localhost'
REDIS_PORT = '6379'
REDIS_DB = '0'
# REDIS_SOCK = '/tmp/redis.sock'

# sock = s.socket(s.AF_UNIX)
# sock.bind(REDIS_SOCK)

CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

ROOT_DIR = os.path.abspath(os.path.curdir)
MAPPING_DIR = f'{ROOT_DIR}/back/hardware'
COMMANDS_DIR = f'{ROOT_DIR}/back/commands'

FILENAMES = 'config', 'focus'

MAPPING_FILE = f'{MAPPING_DIR}/mapping'
COMMANDS_FILE = f'{COMMANDS_DIR}/routines'

CONFIG_FILE = f'{ROOT_DIR}/{FILENAMES[0]}.yml'
BACKUP_FILE = f'{ROOT_DIR}/{FILENAMES[0]}.bak'

LOG_FILE = f'{ROOT_DIR}/{FILENAMES[1]}.log'
DB_FILE = os.getenv('DB_LOCAL', f'{FILENAMES[1]}.db')
