import argparse
import time

import paho.mqtt.client as mqtt

parser = argparse.ArgumentParser()
parser.add_argument("--broker", default="localhost")
parser.add_argument("--port", type=int, default=1883)
parser.add_argument("--qos", type=int, default=1, choices=[0, 1, 2])
args = parser.parse_args()

raise NotImplementedError("TODO Ex2: subscribe to both filters in on_connect and print the topic levels in on_message")
