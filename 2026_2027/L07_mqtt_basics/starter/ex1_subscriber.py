import argparse
import time

import paho.mqtt.client as mqtt

parser = argparse.ArgumentParser()
parser.add_argument("--topic", default="smarthome/house1/kitchen/temperature")
parser.add_argument("--broker", default="localhost")
parser.add_argument("--port", type=int, default=1883)
args = parser.parse_args()


raise NotImplementedError("TODO Ex1: write on_connect/on_message, create the client, connect, loop_start")
