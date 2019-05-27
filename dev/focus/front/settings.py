import os


class BaseConfig:
    TESTING = False
    SECRET_KEY = os.getenv(
        'SK',
        r'f0cu526980u_ps3%2Bnr0q9%25cg%5E%3D%2Bqec%40uq73tl%299b%40%40w-9r3%29%40exz%40iopr0'
    )


class DevelopmentConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = 'dev'


class TestingConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = 'test'


_ = {
    'postgres': {
        'dbapi': 'psycopg2',
        'user': 'postgres',
        'password': 'postgres',
        'host': '',
        'name': 'mydb',
    },
    'mysql': {
        'dbapi': 'mysqlconnector',
        'user': 'FocusCore',
        'password': os.getenv('FC'),
        'host': '',
        'name': 'focus_test',
    },
    'sqlite': {
        'path': '/tmp/test.db',
    },
}

DATABASES = {
    'default': 'postgresql+%s://%s:%s@%s/%s' % (
        _['postgres']['dbapi'],
        _['postgres']['user'],
        _['postgres']['password'],
        _['postgres']['host'],
        _['postgres']['name'],
    ),
    'mysql': 'mysql+%s://%s:%s@%s/%s' % (
        _['mysql']['dbapi'],
        _['mysql']['user'],
        _['mysql']['password'],
        _['mysql']['host'],
        _['mysql']['name'],
    ),
    'sqlite': 'sqlite:///%s' % (_['sqlite']['path'])
}


##### SQLAlchemy setup #####
BaseConfig._db = os.getenv('DB', 'default')
BaseConfig.SQLALCHEMY_DATABASE_URI = DATABASES[_db]
BaseConfig.SQLALCHEMY_TRACK_MODIFICATIONS = False

DevelopmentConfig.SQLALCHEMY_TRACK_MODIFICATIONS = True

TestingConfig.SQLALCHEMY_DATABASE_URI = DATABASES['sqlite']
TestingConfig.SQLALCHEMY_TRACK_MODIFICATIONS = True


##### Flask-Admin setup #####
BasicConfig.BASIC_AUTH_USERNAME = 'admin'
BasicConfig.BASIC_AUTH_PASSWORD = 'admin'
