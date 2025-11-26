import time

import paho.mqtt.client as mqtt


class Sub:
    def __init__(self, client_id):
        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=client_id
        )
        self.client.on_message = self.notify

    def notify(self, client, userdata, msg):
        print(f"message : {msg.payload} from topic : {msg.topic} with qos:{msg.qos}")

    def start(self, broker, port):
        self.client.connect(broker, port)
        self.client.loop_start()

    def subscribe(self, topic, qos):
        self.client.subscribe(topic, qos)

    def unsubscribe(self, topic):
        self.client.unsubscribe(topic)

    def finalize(self):
        self.client.loop_stop()
        self.client.disconnect()


if __name__ == "__main__":
    broker = "test.mosquitto.org"
    port = 1883
    client_id = "Pi4948738"
    topic = "exercises/helloworld"

    sub = Sub(client_id)
    sub.start(broker, port)
    sub.subscribe(topic, qos=0)

    i = 0
    while True:
        time.sleep(1)
        i += 1
        if i == 1000:
            break
    sub.unsubscribe(topic)
    sub.finalize()
