from paho.mqtt import client

class MQTT_client():
    def __init__(self, client_id):
        self.client_id = client_id
        self.client = client.Client(callback_api_version=client.CallbackAPIVersion.VERSION2, client_id= self.client_id)
    
    def register_callbacks(self, on_con = None, on_dis = None, on_pub=None, on_mess=None):
        if on_con:
            self.client.on_connect = on_con
        if on_dis:
            self.client.on_disconnect = on_dis
        if on_pub:
            self.client.on_publish = on_pub
        if on_mess:
            self.client.on_message = on_mess

    def start(self, broker, port):
        self.client.connect(broker, port)
        self.client.loop_start()
    
    def publish(self, topic, msg, qos=0):
        self.client.publish(topic, msg, qos)
    
    def subscribe(self, topic, qos=0):
        self.client.subscribe(topic, qos=qos)