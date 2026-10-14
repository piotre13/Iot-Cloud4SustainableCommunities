import argparse
import time

import paho.mqtt.client as mqtt

parser = argparse.ArgumentParser()
parser.add_argument("--broker", default="localhost")
parser.add_argument("--port", type=int, default=1883)
parser.add_argument("--qos", type=int, default=1, choices=[0, 1, 2])
args = parser.parse_args()

# '+' = exactly one level, '#' = everything below (only at the end)
FILTERS = ["smarthome/+/+/temperature", "smarthome/#"]


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"connected ({reason_code})")
    for topic_filter in FILTERS:
        client.subscribe(topic_filter, qos=args.qos)


def on_message(client, userdata, msg):
    levels = msg.topic.split("/")
    print(f"{msg.topic} levels={levels} qos={msg.qos} payload={msg.payload.decode()}")
    if len(levels) == 4:
        print(f"   house={levels[1]} room={levels[2]} quantity={levels[3]}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ex2_wildcards")
client.on_connect = on_connect
client.on_message = on_message
client.connect(args.broker, args.port)
client.loop_start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    client.loop_stop()
    client.disconnect()
