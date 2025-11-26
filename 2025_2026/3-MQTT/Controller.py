from MyMQTT import MQTTclient
import time



class Controller():
    def __init__ (self, client_id, broker, port):
        self.client = MQTTclient(client_id, broker, port)
        self.client.register_callbacks(on_mes=self.trigger)
        self.client.start()

        self.memory = {}
        self.thresholds = {} 


    def trigger(self, client, userdata, msg):
        pass


    def run(self, topics, freq=1):
        for topic, qos in topics.items():
            self.client.subscribe(topic, qos)
            self.memory[topic]=[]

        while True:
            time.sleep(1)



if __name__ == '__main__':
    cl_id = 'djdhdhgs'
    broker = ' test.mosquitto.org'
    port = 1883
    topics = {'kitchen/sens1':0,'kitchen/sens2':0 }

    controller = Controller(cl_id,broker, port)

    controller.run()