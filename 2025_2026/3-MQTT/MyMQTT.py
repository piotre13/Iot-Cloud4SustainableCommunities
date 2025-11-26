import paho.mqtt.client as mqtt


class MQTTclient():
    def __init__(self, client_id, broker, port):
        self.client_id = client_id
        self.broker = broker
        self.port = port
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    

    def register_callbacks(self, on_con=None, on_dis= None, on_pub = None, on_mes=None):
        if on_con:
            self.client.on_connect = on_con
        if on_dis:
            self.client.on_disconnect = on_dis
        if on_pub:
            self.client.on_publish = on_pub
        if on_mes:
            self.client.on_message = on_mes


    def start(self):
        self.client.connect(self.broker, self.port)
        self.client.loop_start()

    def publish(self, topic, message, qos=0):
        self.client.publish(topic, message, qos)


    def subscribe(self, topic, qos):
        self.client.subscribe(topic, qos)
    
    def unsubscribe(self, topic):
        self.client.unsubscribe(topic)

    def finalize(self):
        self.client.disconnect()
        self.client.loop_stop()