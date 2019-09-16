import asyncio
import os

from flask import Flask

from focus.back import FocusPro

app = Flask(__name__)
focus_pro = FocusPro()
timeout = os.getenv('TIMEOUT', 0)

if __name__ == "__main__":
    from . import models, views

    focus_pro.connect_async(timeout)


if os.getenv('FLASK_ENV') == 'development':
    from gpiozero import Device
    from gpiozero.pins.mock import MockFactory

    Device.pin_factory = MockFactory()
