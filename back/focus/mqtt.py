import json

import paho.mqtt.client as mqtt


def on_connect(client, userdata, rc):
    client.subscribe("$SYS/#")


def on_message(client, userdata, msg):
    print(msg.title, json.loads(msg.payload))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect('89.223.27.69')