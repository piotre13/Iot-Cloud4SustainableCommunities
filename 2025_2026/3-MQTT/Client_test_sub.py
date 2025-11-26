from MqttClient import MQTT_client
import time as tm
class Client_sub():
    def __init__(self, client_id):
        self.client_id = client_id
        self.client = MQTT_client(self.client_id)
        self.storage = {}
    def notify(self, client, userdata, message):
        print(f"message received msg={message.payload} at topic={message.topic}")
        
    
    def run (self, time, topics, broker, port):
        self.client.start(broker, port)
        self.client.register_callbacks(on_mess=self.notify)
        for topic, qos, in topics.items():
            self.client.subscribe(topic,qos)

        t=0
        while True:
            tm.sleep(1)
            if t==time:
                break
            t+=1



if __name__ == '__main__':
    broker_addr = "127.0.0.1"
    port = 1883
    client_id = "Subscriber3434"
    topics={"exercises/helloworld":0}
    sub = Client_sub(client_id=client_id)
    sub.run(time=100, topics=topics, broker=broker_addr, port=port)