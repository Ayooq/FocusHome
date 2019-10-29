import paho.mqtt.client as mqtt
import gzip


snmp_data = """
.1.3.6.1.2.1.1.1.0 = STRING: "KYOCERA Document Solutions Printing System"
.1.3.6.1.2.1.1.2.0 = OID: .1.3.6.1.4.1.1347.41
"""



# gzip_bytes - передать в mqtt
gzip_bytes = gzip.compress(snmp_data.encode())

print(type(gzip_bytes), len(gzip_bytes), len(snmp_data))
#data = gzip.decompress(gzip_bytes).decode()
#print(data)
#print(gzip_bytes)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("+/snmp/+")

    client.publish("FP-1/snmp/image", gzip_bytes)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    pass#print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("89.223.27.69", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()