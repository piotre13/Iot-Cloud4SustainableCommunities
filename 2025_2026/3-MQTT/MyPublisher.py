import time

import paho.mqtt.client as mqtt


class MyPub:
    def __init__(
        self,
        broker_address= None,
        broker_port= None,
        client_id= None,
    ):
        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=client_id
        )

        # register callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        self.client.connect(broker_address, broker_port)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print("Connected with result code " + str(reason_code))

    def on_disconnect(self, client, userdata, reason_code, properties):
        print("Disconnected with result code " + str(reason_code))

    def on_publish(self, client, userdata, mid, reason_code, properties):
        print("Message published with mid " + str(mid))

    def publish(self, topic, payload, qos=0):
        self.client.publish(topic, payload, qos)

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()


if __name__ == "__main__":
    publisher = MyPub(broker_address="test.mosquitto.org", broker_port=1883)
    try:
        i = 0
        while True:
            message = f"Hello MQTT {i}"
            publisher.publish("test/topic", message, qos=1)
            i += 1
            if i >= 20:
                break
            time.sleep(2)
    finally:
        publisher.stop()
