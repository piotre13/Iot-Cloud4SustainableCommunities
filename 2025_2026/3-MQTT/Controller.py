from MyMQTT import MQTTclient
import time



class Controller():
    def __init__ (self, client_id, broker, port):
        self.client = MQTTclient(client_id, broker, port)
        self.client.register_callbacks(on_mes=self.trigger)
        self.client.start()

        self.memory = {}
        self.thresholds = {} 
        self.act_topics={}


    def trigger(self, client, userdata, msg):
        print(f"message : {msg.payload} from topic : {msg.topic} with qos:{msg.qos}")
        self.memory[msg.topic].append(msg.payload[0]['v'])

       


    def run(self, topics, freq=1):
        for topic, qos in topics.items():
            self.client.subscribe(topic, qos)
            self.memory[topic]=[]

        while True:

            self.thresholds = {'kitchen/sens1':200,'living_romm/sens2':400 }     #this must be substistuted with 
            self.act_topics = {'kitchen/sens1':'kitchen/act1','living_romm/sens2':'living_room/act2' }
            # a GET request  both of them 
            # self.thresholds = requests.get('url') 
            # self.act_topics = requests.get('url') 

            for topic, vals in self.memory.items():
                if vals:
                    avg_val = sum(vals)/len(vals)
                    if avg_val < self.thresholds[topic]:
                        # do something
                        self.client.publish(self.act_topics[topic], 'ON', qos=0)

            time.sleep(freq)



if __name__ == '__main__':
    cl_id = 'djdhdhgs'
    broker = ' test.mosquitto.org'
    port = 1883
    topics = {'kitchen/sens1':0,'living_romm/sens2':0 }

    controller = Controller(cl_id,broker, port)

    controller.run(freq=10)