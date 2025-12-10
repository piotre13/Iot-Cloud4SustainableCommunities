from MyMQTT import MQTTclient
import time
import requests

class LightSwitch():
    def __init__(self, cat_reg, room):
        body = {'room_name':room, 'type':'actuator'}
        res = requests.post(cat_reg, json=body)
        data = res.json()
        self.broker = data['broker']
        self.port = data['port']
        self.id = data['unique_id']
        self.topic = data['topic']

        self.client = MQTTclient(self.id, self.broker, self.port)
        self.client.register_callbacks(on_mes= self.actuate)
        self.client.start()
        self.client.subscribe(self.topic, qos=0)

        self.state = False


    def actuate(self,client, user_data, msg):
        data = msg.payload

        if data == 'ON' and self.state == False:
            self.state = True

        if data =='OFF' and self.state == True:
            self.state = False
    
    def run(self):
        while True:
            print(f'LightSwitch {self.id} in state: {self.state}')
            time.sleep(5)
         


if __name__ =='__main__':
    cat_url = 'localhost:8080/project/register'
    act = LightSwitch(cat_url, 'kitchen')
    act.run()