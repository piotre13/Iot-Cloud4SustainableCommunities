from MyMQTT import MQTTclient
import time
import requests
import random
import json

class LightSensor:
    def __init__ (self,catalog_reg_end, room):
        body ={'room_name':room, 'type':'sensor'}
        res =  requests.post(catalog_reg_end,json = body ) 
        data = res.json()
        self.broker = data['broker']
        self.port = data['port']
        self.topic = data['topic']
        self.id =data['unique_id']


        self.client = MQTTclient(self.id, self.broker, self.port)
        self.client.start()

    def run (self, freq):
        while True:
            val = random.randint(0,1000)
            msg = [{'bn':self.id,
                    'n': 'light',
                     't':time.time(),
                      'v': val }]
            self.client.publish(self.topic,json.dumps(msg), qos=0)
            time.sleep(freq)

        

if __name__ == '__main__':
    cat_register = 'localhost:8080/project/register'
    sens1 = LightSensor(cat_register, 'kitchen')
    sens1.run()
        
