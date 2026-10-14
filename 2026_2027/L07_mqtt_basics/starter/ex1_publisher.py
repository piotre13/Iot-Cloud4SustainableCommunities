import argparse
import random
import time

import paho.mqtt.client as mqtt

parser = argparse.ArgumentParser()
parser.add_argument("--topic", default="smarthome/house1/kitchen/temperature")
parser.add_argument("--broker", default="localhost")
parser.add_argument("--port", type=int, default=1883)
args = parser.parse_args()

raise NotImplementedError("TODO Ex1: create the paho v2 client, connect, loop_start, publish a temperature every 2 s")
