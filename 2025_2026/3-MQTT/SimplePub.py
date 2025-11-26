import time

from paho.mqtt import client as mqtt


class Pub:
    def __init__(self, client_id, broker, port):
        self.client_id = client_id
        self.broker = broker
        self.port = port

        # instance of client class
        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.client_id,
        )

        # registering callbacks
        self.client.on_connect = self.My_on_connect
        self.client.on_publish = self.My_on_publish

        # connect to broker
        self.client.connect(self.broker, self.port)


        # start the loop
        self.client.loop_start()

    def publish(self, topic, msg, qos=0):
        self.client.publish(topic, msg, qos)

    def My_on_connect(self, client, userdata, flags, reason_code, properties):
        print("Succesfully connected to broker")

    def My_on_publish(self, client, userdata, mid, reason_code, properties):
        print(f"Published message with message_id = {mid}")

    def finalize(self):
        self.client.loop_stop()
        self.client.disconnect()


if __name__ == "__main__":
    broker_addr = "test.mosquitto.org"
    port = 1883
    client_id = "Pietro_icss647467"
    pub = Pub(client_id, broker_addr, port)
    for i in range(100):
        pub.publish("exercises/helloworld", "Helloworld%i" % i)
        time.sleep(2)

    pub.finalize()
