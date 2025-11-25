import time

import paho.mqtt.client as mqtt

[
  {
    "bn": "http://example.org/sensor1/",
    "n": "temperature",
    "u": "Cel",
    "t": 1234,
    "v": 22.5
  }
]

class MySub:
    def __init__(
        self,
        broker_address="localhost",
        broker_port=1883,
        client_id="default_subscriber",
    ):
        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=client_id
        )

        # register callbacks
        self.client.on_connect = self.on_connect
        # self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        self.client.connect(broker_address, broker_port)
        self.client.loop_start()

        # subscribe to topic
        self.client.subscribe("test/topic", qos=1)

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print("Connected with result code " + str(reason_code))

    def on_disconnect(self, client, userdata, rc):
        print("Disconnected with result code " + str(rc))

    def on_message(self, client, userdata, msg):
        print(f"Message received on topic {msg.topic}: {msg.payload.decode()}")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()


if __name__ == "__main__":
    subscriber = MySub(broker_address="test.mosquitto.org", broker_port=1883)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        subscriber.stop()
