from flask import Flask, render_template, request
from iron import Irons

app = Flask(__name__)

irn = Irons()

banka = irn.config['banka']

from app import models
from app import views
