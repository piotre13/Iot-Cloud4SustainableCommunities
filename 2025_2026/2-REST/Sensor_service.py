import sys
sys.path.append('2025_2026/1-OOP/')
from LightSensor1 import LightSensor1

import cherrypy
import time
import threading


class Sensors:
    exposed=True
    def __init__(self):
        self.sensors = []
        self.catalog = {}


    @cherrypy.tools.json_out()
    def GET(self, *uri,**params):
        if uri[0] == 'sensors':
            if params:
                return self.catalog[params['k']]
            else:
                return self.catalog


    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self, *uri, **params):
        body = cherrypy.request.json
        sens_id= 'Light_sens%i'%len(self.sensors)
        sens = LightSensor1(sens_id, body['room'])
        self.sensors.append(sens)
        self.catalog[sens_id]={'name':body['name'],
                               'register_time':time.time(),
                               'room':body['room'],
                               'memory':sens.sensed}
        target = threading.Thread(target = sens.run, args= (body['time_steps'], body['freq']) )
        target.start()
        # sens.run(body['time_steps'], body['freq'])



if __name__ == '__main__':
    conf = {
        "/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
            "tools.sessions.on": True,
        }
    }

    cherrypy.tree.mount(Sensors(), "/", conf)

    cherrypy.engine.start()
    cherrypy.engine.block()