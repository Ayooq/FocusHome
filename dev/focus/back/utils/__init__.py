import os


ROOT_DIR = os.path.abspath(os.path.curdir)
CONFIG_FILE = '%s/config.yaml' % ROOT_DIR
LOG_FILE = '%s/focus.log' % ROOT_DIR
DB_FILE = os.getenv('DB_LOCAL', 'focus.db')
