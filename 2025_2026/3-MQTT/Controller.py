import json
import time

import requests
from MyMQTT import MQTTclient


class Controller:
    def __init__(self, client_id, broker, port, th_url="", pairs_url=""):
        self.client = MQTTclient(client_id, broker, port)
        self.client.register_callbacks(on_mes=self.trigger)
        self.client.start()

        self.th_url = th_url
        self.pairs_url = pairs_url

        self.memory = {}
        self.thresholds = {}
        self.act_topics = {}

    def trigger(self, client, userdata, msg):
        data = json.loads(msg.payload)
        print(f"message : {data} from topic : {msg.topic} with qos:{msg.qos}")

        self.memory[msg.topic].append(data[0]["v"])

    def run(self, topics, freq=1):
        for topic, qos in topics.items():
            self.client.subscribe(topic, qos)
            self.memory[topic] = []

        while True:
            # a GET request  both of them
            self.thresholds = requests.get(self.th_url).json()
            self.act_topics = requests.get(self.pairs_url).json()
            print(self.act_topics)
            # self.act_topics = requests.get('url')

            for topic, vals in self.memory.items():
                if vals:
                    avg_val = sum(vals) / len(vals)
                    if avg_val < self.thresholds[topic]:
                        cmd = {"command": "ON"}
                        # do something
                        self.client.publish(self.act_topics[topic], json.dumps(cmd), qos=0)
                        print(f'publish message on topic:{self.act_topics[topic]}')

            time.sleep(freq)


if __name__ == "__main__":
    cl_id = "djdhdhgs"
    broker = "localhost"
    port = 1883
    topics = {"house1/kitchen/sens_0": 0}

    th_enpoint = "http://localhost:8080/house1/thresholds"
    pairs_endpoint = "http://localhost:8080/house1/pairs"

    controller = Controller(cl_id, broker, port, th_enpoint, pairs_endpoint)

    controller.run(topics=topics, freq=5)
