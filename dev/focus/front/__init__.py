import os

from flask import Flask

from focus.back import FocusPro
from focus.back.commands.handle import Handler

app = Flask(__name__)

if os.getenv('FLASK_ENV') == 'development':
    from gpiozero import Device
    from gpiozero.pins.mock import MockFactory

    Device.pin_factory = MockFactory()

countdown = os.getenv('COUNTDOWN', 0)
focus_pro = FocusPro()
focus_pro.handler = Handler(focus_pro)
focus_pro.connect_async(int(countdown))
focus_pro.client.loop_start()

from . import views
