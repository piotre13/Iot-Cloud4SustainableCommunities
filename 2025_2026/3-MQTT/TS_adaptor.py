import json
import time

import requests
from MyMQTT import MQTTclient

WRITE_API_KEY = "<your_write_api_key>"


class TS_adaptor:
    def __init__(self, client_id, broker, port):
        self.client = MQTTclient(client_id, broker, port)
        self.client.register_callbacks(on_mes=self.memory)
        self.client.start()
        self.client.subscribe("house1/kitchen/sens_0", qos=0)

        self.data = {"field1": []}

    def memory(self, client, userdata, msg):
        data = json.loads(msg.payload)
        val = data[0]["v"]
        res = requests.get(
            f"https://api.thingspeak.com/update?api_key={WRITE_API_KEY}&field1={val}"
        )


if __name__ == "__main__":
    broker = "localhost"
    port = 1883
    c_id = "ahajkshjshsjs"
    Ts = TS_adaptor(c_id, broker, port)
    while True:
        time.sleep(3)
