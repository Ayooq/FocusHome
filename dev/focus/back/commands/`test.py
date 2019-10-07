import json
from focus.back import FocusPro, Handler
from gpiozero import Device
from gpiozero.pins.mock import MockFactory
Device.pin_factory = MockFactory()
focus = FocusPro()
focus.handler = Handler(focus)
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

{"device_id": "1", "routine_id": 14, "routine_name": "включение вентилятора малинки", "routine_comment": "на малинке должна существоввать функция run_fan(speed, min_temp)\nIF (in1 = \"0\" and in2 = \"1\") or cpu > \"80\" THEN\n    call run_fan(speed=\"500\" ,min_temp=\"60\" );\nEND IF;", "instruction": {"routine": {"conditions": [
    [{"unit": "in1", "compare": "eq", "value": "0"}, "and", {"unit": "in2", "compare": "eq", "value": "1"}], "or", {"unit": "cpu", "compare": "gt", "value": "80"}], "actions": [{"action": "call", "unit": "", "value": "", "function": "run_fan", "params": [{"name": "speed", "value": "500"}, {"name": "min_temp", "value": "60"}]}]}}}
