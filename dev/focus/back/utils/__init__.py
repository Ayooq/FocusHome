import os

ROOT_DIR = os.path.abspath(os.path.curdir)

CONFIG_FILE = f'{ROOT_DIR}/config.yaml'
BACKUP_FILE = f'{ROOT_DIR}/config.yaml.bak'
LOG_FILE = f'{ROOT_DIR}/focus.log'
DB_FILE = os.getenv('DB_LOCAL', 'focus.db')

BROKER = {
    'host': '89.223.27.69',
    'port': 1883,
    'keepalive': 60,
}
