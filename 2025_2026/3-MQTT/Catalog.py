import cherrypy


class Catalog:
    exposed = True
    def __init__(self):
        self.data = {"broker":'test.mosquitto.org',
                     "port": 1883,
                     "base_topic":'house1',
                     "thresholds": [{"room":'kitchen', "val": 200 }, {"room":'living_room', 'val': 300}],
                     "rooms":[{"room_name": "kitchen", "sensors":[], "actuators":[]}]
                     }

    @cherrypy.tools.json_in()    
    def POST(self, *uri, **params):
        data =  cherrypy.request.json

        for room in self.data['rooms']:
            if room['room_name'] == data['room_name']:
                if data['type'] == 'sensor' and len(room['sensors'])==0:
                    sens_id = f'{room['room_name']}_sens{len(room['sensors'])}'
                    topic = self.data['base_topic']+'/'+room['room_name']+'/'+'sens_%i'%len(room['sensors'])
                    room['sensors'].append({'sens_name':sens_id, 'topic':topic})
                    return {"broker":self.data['broker'], "port": self.data['port'], 'topic':topic, 'unique_id':sens_id }
                
                if data['type'] == 'actuator' and len(room['actuators'])==0:
                    act_id = f'{room['room_name']}_sens{len(room['actuators'])}'
                    topic = self.data['base_topic']+'/'+room['room_name']+'/'+'act_%i'%len(room['actuators'])
                    room['actuators'].append({'act_name':sens_id, 'topic':topic})
                    return {"broker":self.data['broker'], "port": self.data['port'], 'topic':topic, 'unique_id':act_id }
                
                
    def GET(self, *uri, **params):
        return self.data
    

if __name__ == '__main__':


