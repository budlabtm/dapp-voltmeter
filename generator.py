import paho.mqtt.client as mqtt
import random
import time
import numpy

client = mqtt.Client()

client.username_pw_set("username", "password")
client.connect("192.168.0.21")

i = 0

while True:
    if i == 8000:
        i = 1
    else:
        i += 1

    client.publish("/test/c0", 512 + 64 * numpy.cos(i * 10 / 256) +
                   32 * numpy.cos(i * 30 / 512) + random.randint(0, 8))

    client.publish("/test/c1", 512 + 64 * numpy.cos(i * 10 / 256) +
                   32 * numpy.cos(i * 30 / 512) + random.randint(0, 8))

    time.sleep(1 / 200)
