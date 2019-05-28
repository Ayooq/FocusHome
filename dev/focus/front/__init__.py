import os
import uuid

from flask import Flask

from focus.back.connect import Connector


def create_app(config_filename):
    app = Flask(__name__)
    configure_app(app)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import views

    return app


def configure_app(app):
    _mode = os.getenv('FLASK_ENV', 'default')

    if _mode == 'production':
        app.config.from_object(CONFIG['default'])
        set_envcfg(app)
    else:
        app.config.from_object(CONFIG[_mode])


def set_envcfg(app):
    app.config.from_envvar('PRODS', silent=True)

    if not app.config['SECRET_KEY']:
        app.secret_key = uuid.uuid4().hex


CONFIG = {
    'default': '%s.settings.BaseConfig' % __name__,
    'development': '%s.settings.DevelopmentConfig' % __name__,
    'testing': '%s.settings.TestingConfig' % __name__,
    'production': None,
}

conn = Connector()
conn.client.loop_start()
device = conn.config['device']
