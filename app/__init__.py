from flask import Flask, render_template, request
from iron import Connector
#   from iron import Irons

app = Flask(__name__)

irn = Connector()
irn.client.loop_start()

banka = irn.config['banka']

from app import models
from app import views
