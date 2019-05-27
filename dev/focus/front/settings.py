import os


class BaseConfig:
    TESTING = False
    SECRET_KEY = 'dev'


class DevelopmentConfig(BaseConfig):
    TESTING = True


class TestingConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = 'test'


_ = {
    'postgres': {
        'dbapi': os.getenv('PGDBAPI', 'psycopg2'),
        'user': os.getenv('PGDBUSER', 'postgres'),
        'password': os.getenv('PGDBPASS', 'postgres'),
        'host': os.getenv('PGDBHOST', ''),
        'name': os.getenv('PGDBNAME', 'mydb'),
    },
    'mysql': {
        'dbapi': os.getenv('MYDBAPI', 'mysqlconnector'),
        'user': os.getenv('MYDBUSER', 'mysql'),
        'password': os.getenv('MYDBPASS', 'mysql'),
        'host': os.getenv('MYDBHOST', ''),
        'name': os.getenv('MYDBNAME', 'mydb'),
    },
    'sqlite': {
        # 'path': r'C:\\tmp\test.db',
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
_db = os.getenv('DB', 'default')
BaseConfig.SQLALCHEMY_DATABASE_URI = DATABASES[_db]
BaseConfig.SQLALCHEMY_TRACK_MODIFICATIONS = False

DevelopmentConfig.SQLALCHEMY_TRACK_MODIFICATIONS = True

TestingConfig.SQLALCHEMY_DATABASE_URI = DATABASES['sqlite']
TestingConfig.SQLALCHEMY_TRACK_MODIFICATIONS = True
