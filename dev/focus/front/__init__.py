from flask import Flask

from focus.back import Connector


app = Flask(__name__)

c = Connector()
device = c.config['device']

from . import views, models
