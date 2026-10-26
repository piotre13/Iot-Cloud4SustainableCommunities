import argparse
import time

from devices import HumiditySensor, TemperatureSensor
from mymqtt import MyMQTT
from senml import senml_record

parser = argparse.ArgumentParser()
parser.add_argument("house")
parser.add_argument("room")
parser.add_argument("--interval", type=float, default=5)
parser.add_argument("--broker", default="localhost:1883", help="host:port")
args = parser.parse_args()

raise NotImplementedError("TODO Ex4: publish SenML temperature and humidity records with MyMQTT every --interval seconds")
