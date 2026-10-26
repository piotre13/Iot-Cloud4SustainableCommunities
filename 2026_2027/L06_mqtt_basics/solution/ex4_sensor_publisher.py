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

host, port = args.broker.split(":")
client = MyMQTT(f"sensors_{args.house}_{args.room}", host, int(port))
client.start()

sensors = [TemperatureSensor(), HumiditySensor()]
try:
    while True:
        for sensor in sensors:
            record = senml_record(f"{args.house}/{args.room}", sensor.name, sensor.unit, sensor.sense())
            topic = f"smarthome/{args.house}/{args.room}/{sensor.name}"
            client.publish(topic, record)
            print(topic, record)
        time.sleep(args.interval)
except KeyboardInterrupt:
    pass
finally:
    client.stop()
