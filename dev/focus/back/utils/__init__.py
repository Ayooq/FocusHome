import os

ROOT_DIR = os.path.abspath(os.path.curdir)

CONFIG_FILE = '%s/config.yaml' % ROOT_DIR
BACKUP_FILE = '%s/config.yaml.bak' % ROOT_DIR
LOG_FILE = '%s/focus.log' % ROOT_DIR
DB_FILE = os.getenv('DB_LOCAL', 'focus.db')

BROKER = {
    'host': '89.223.27.69',
    'port': 1883,
    'keepalive': 60,
}
