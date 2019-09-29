import paho.mqtt.client as mqtt

broker_url = "192.168.1.108"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

def woof():
    client.publish(topic="DAD1-cpu", payload="30", qos=0, retain=False)

woof()