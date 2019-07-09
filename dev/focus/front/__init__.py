import os

from flask import Flask

from focus.back import Connector


app = Flask(__name__)

if os.getenv('FLASK_ENV') == 'development':
    from gpiozero import Device
    from gpiozero.pins.mock import MockFactory

    Device.pin_factory = MockFactory()

c = Connector()

from . import views, models
