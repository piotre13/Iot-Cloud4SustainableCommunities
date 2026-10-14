import json
import traceback

import paho.mqtt.client as mqtt


class MyMQTT:
    """Small paho-mqtt v2 wrapper: JSON payloads, a notifier object, re-subscribe on reconnect.

    The notifier is any object with a method notify(topic, payload) where payload is a dict.
    """

    def __init__(self, client_id, broker, port, notifier=None):
        self.client_id = client_id
        self.broker = broker
        self.port = port
        self.notifier = notifier
        self.topics = set()
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"[{self.client_id}] connected to {self.broker}:{self.port} ({reason_code})")
        # after a broker restart the session is gone: subscribe again
        for topic in list(self.topics):  # copy: subscribe() may add topics from another thread
            self.client.subscribe(topic, qos=1)

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload)
        except json.JSONDecodeError:
            print(f"Ignored non-JSON message on {msg.topic}")
            return
        if self.notifier is None:
            return
        try:
            self.notifier.notify(msg.topic, payload)
        except Exception:
            # an exception here would stop paho's network loop: report it and keep the client alive
            traceback.print_exc()

    def start(self):
        self.client.connect(self.broker, self.port)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, topic, payload, qos=1):
        self.client.publish(topic, json.dumps(payload), qos=qos)

    def subscribe(self, topic, qos=1):
        self.topics.add(topic)
        self.client.subscribe(topic, qos=qos)

    def unsubscribe(self, topic):
        self.topics.discard(topic)
        self.client.unsubscribe(topic)
