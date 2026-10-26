import argparse
import random
import time

import paho.mqtt.client as mqtt

parser = argparse.ArgumentParser()
parser.add_argument("--topic", default="smarthome/house1/kitchen/temperature")
parser.add_argument("--broker", default="localhost")
parser.add_argument("--port", type=int, default=1883)
args = parser.parse_args()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ex1_publisher")
client.connect(args.broker, args.port)
client.loop_start()  # network loop in a background thread

try:
    while True:
        value = round(random.uniform(15, 28), 1)
        client.publish(args.topic, str(value))
        print(f"published {value} on {args.topic}")
        time.sleep(2)
except KeyboardInterrupt:
    pass
finally:
    client.loop_stop()
    client.disconnect()
