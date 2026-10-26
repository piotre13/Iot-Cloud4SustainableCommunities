import argparse
import random
import time

from mymqtt import MyMQTT


class Printer:
    """Notifier: MyMQTT calls notify() for every JSON message received."""

    def notify(self, topic, payload):
        print(f"received on {topic}: {payload}")


parser = argparse.ArgumentParser()
parser.add_argument("--broker", default="localhost")
parser.add_argument("--port", type=int, default=1883)
args = parser.parse_args()

client = MyMQTT("ex3_demo", args.broker, args.port, Printer())
client.start()
client.subscribe("smarthome/house1/+/temperature")

try:
    while True:
        client.publish("smarthome/house1/kitchen/temperature", {"value": round(random.uniform(15, 28), 1)})
        time.sleep(2)
except KeyboardInterrupt:
    pass
finally:
    client.stop()
