import json
import os
from focus.back import FocusPro, Handler
from gpiozero import Device
from gpiozero.pins.mock import MockFactory
Device.pin_factory = MockFactory()
countdown = os.getenv('COUNTDOWN', 0)
focus = FocusPro()
focus.handler = Handler(focus)
snmp = focus.config['snmp']
snmp_config_data = {
    'target': snmp['agent'],
    'oids': snmp['oids'],
    'credentials': snmp['credentials'],
    'port': snmp['port'],
    'count': '1.3.6.1.2.1.2.1.0',
    'start_from': 0,
}
focus.handler.execute_command(
    '-1', [('self', 'snmp_send_data', snmp_config_data)])
focus.connect_async(int(countdown))
focus.client.loop_start()
payload1 = json.loads(
    '{"routine_id": 2, "instruction": {"routine": {"conditions": [[{"unit": "cnt1", "compare": "eq", "value": "1"}, "and", {"unit": "cnt2", "compare": "eq", "value": "0"}], "or", {"unit": "cpu", "compare": "gt", "value": "80.0"}], "actions": [{"action": "setValue", "unit": "cnt2", "value": "1", "function": "", "params": []}]}}}')
payload2 = json.loads(
    '{"routine_id": 3, "instruction": {"routine": {"conditions": [[{"unit": "cnt1", "compare": "eq", "value": "1"}, "and", {"unit": "cnt2", "compare": "eq", "value": "1"}], "or", {"unit": "cpu", "compare": "ge", "value": "60.0"}], "actions": [{"action": "call", "unit": "lock", "value": "", "function": "on", "params": []}, {"action": "call", "unit": "self", "value": "", "function": "reboot", "params": []}]}}}')
payload3 = json.loads(
    '{"routine_id": 4, "instruction": {"routine": {"conditions": [[{"unit": "lock", "compare": "eq", "value": "1"}]], "actions": [{"action": "call", "unit": "cnt4", "value": "", "function": "toggle", "params": []}]}}}')
instructions1 = focus.parser.parse_instructions(
    focus, payload1, focus.hardware)
instructions2 = focus.parser.parse_instructions(
    focus, payload2, focus.hardware)
instructions3 = focus.parser.parse_instructions(
    focus, payload3, focus.hardware)
focus.handler.handle(instructions1)
focus.handler.handle(instructions2)
focus.handler.handle(instructions3)
focus.couts['cnt1'].on()
