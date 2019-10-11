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

snmp = focus_pro.config['snmp']
snmp_config_data = {
    'target': snmp['agent'],
    'oids': snmp['oids'],
    'credentials': snmp['credentials'],
    'port': snmp['port'],
    'count': '1.3.6.1.2.1.2.1.0',
    'start_from': 0,
}

focus_pro.handler.execute_command(
    '-1', [('self', 'snmp_send_data', snmp_config_data)])
focus_pro.connect_async(int(countdown))
focus_pro.client.loop_start()

from . import views
