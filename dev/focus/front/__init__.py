from . import views, models
from flask import Flask

from focus.back import Connector


app = Flask(__name__)

conn = Connector()
device = conn.config['device']
