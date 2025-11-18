import sys
import time
import threading
import cherrypy

sys.path.append("2025_2026/1-OOP")
from LightSensor1 import LightSensor1


class Sensors:
    exposed = True

    def __init__(self):
        self.sensor_store = {}
        self.sensors = []

    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        return self.sensor_store

    # def update_memory(self):
    #     for sens in self.sensors:
    #         sens_id = sens.sensro_id
    #         self.sensor_store[sens_id]['memory'] =

    @cherrypy.tools.json_in()
    def POST(self, *uri, **params):
        body = cherrypy.request.json
        if body["type"] == "light":
            sens_id = "light_sens%i" % len(self.sensors)
            sens = LightSensor1(sens_id, body["room"])
            print(sens.__dict__)
            self.sensors.append(sens)
            self.sensor_store[sens_id] = {
                "type": body["type"],
                "addedd": time.time(),
                "life_duration": body["steps"],
                "frequency": body["freq"],
                "memory": sens.sensed,
            }
            thread = threading.Thread(
                target=self.sensors[-1].run, args=(body['steps'],body['freq'],)
            )
            thread.start()
        return "sensor added"

  

if __name__ == "__main__":
    conf = {
        "/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
            "tools.sessions.on": True,
        }
    }

    cherrypy.tree.mount(Sensors(), "/", conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
