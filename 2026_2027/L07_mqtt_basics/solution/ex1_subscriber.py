import argparse
import time

import paho.mqtt.client as mqtt

parser = argparse.ArgumentParser()
parser.add_argument("--topic", default="smarthome/house1/kitchen/temperature")
parser.add_argument("--broker", default="localhost")
parser.add_argument("--port", type=int, default=1883)
args = parser.parse_args()


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"connected ({reason_code})")
    # subscribing here (not after connect()) also works after a reconnection
    client.subscribe(args.topic)


def on_message(client, userdata, msg):
    print(f"{msg.topic}: {msg.payload.decode()}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ex1_subscriber")
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
