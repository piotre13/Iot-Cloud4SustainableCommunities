import argparse
import random
import time

from mymqtt import MyMQTT


parser = argparse.ArgumentParser()
parser.add_argument("--broker", default="localhost")
parser.add_argument("--port", type=int, default=1883)
args = parser.parse_args()

raise NotImplementedError("TODO Ex3: write the Printer notifier and the publisher loop using MyMQTT")
