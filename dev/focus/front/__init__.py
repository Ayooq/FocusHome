import os

from celery import Celery
from flask import Flask

from focus.back import FocusPro
from focus.back.utils import CELERY_BROKER_URL

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = CELERY_BROKER_URL
# app.config['CELERY_RESULT_BACKEND'] = CELERY_RESULT_BACKEND

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

if os.getenv('FLASK_ENV') == 'development':
    from gpiozero import Device
    from gpiozero.pins.mock import MockFactory

    Device.pin_factory = MockFactory()

focus_pro = FocusPro()

if __name__ == "__main__":
    countdown = os.getenv('COUNTDOWN', 0)
    focus_pro.connect_async(countdown)
