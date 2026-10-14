"""Ex1 - device connector with a REST interface.

Usage: python device_connector.py house1 kitchen 8081

  GET /        measurements of the room + HVAC state
  PUT /hvac    body {"command": "ON"} or {"command": "OFF"}
"""
import sys

import cherrypy

from devices import HVAC, HumiditySensor, TemperatureSensor


class DeviceConnector:
    exposed = True

    def __init__(self, house_id, room_id, sensors, hvac):
        self.house_id = house_id
        self.room_id = room_id
        self.sensors = sensors
        self.hvac = hvac
        self.latest = {}

    def read_sensors(self):
        self.latest = {sensor.name: sensor.sense() for sensor in self.sensors}
        return self.latest

    def actuate(self, command):
        self.hvac.actuate(command)

    # TODO Ex1: GET and PUT below
    @cherrypy.tools.json_out()
    def GET(self, *uri):
        raise NotImplementedError("TODO Ex1: return house_id, room_id, fresh measurements and hvac state; 404 if uri is not empty")

    @cherrypy.tools.json_out()
    def PUT(self, *uri):
        raise NotImplementedError("TODO Ex1: only /hvac; read the JSON body, actuate, return the hvac state; 400 if body or command invalid, 404 otherwise")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Usage: python device_connector.py <house_id> <room_id> <port>")
    house_id, room_id, port = sys.argv[1], sys.argv[2], int(sys.argv[3])

    dc = DeviceConnector(house_id, room_id, [TemperatureSensor(), HumiditySensor()], HVAC())
    conf = {"/": {"request.dispatch": cherrypy.dispatch.MethodDispatcher()}}
    cherrypy.config.update({"server.socket_port": port})
    cherrypy.tree.mount(dc, "/", conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
