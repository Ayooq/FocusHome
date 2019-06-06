from flask import Flask

from focus.back import Connector


app = Flask(__name__)

conn = Connector()
conn.client.loop_start()
device = conn.config['device']

from . import views, models
