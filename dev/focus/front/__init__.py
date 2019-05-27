from flask import Flask

from focus.back.connect import Connector


app = Flask(__name__)

conn = Connector()
conn.client.loop_start()
device = conn.config['device']

from . import views, models

if __name__ == "__main__":
    app.run(host='127.0.0.1')
