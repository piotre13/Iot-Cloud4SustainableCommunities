import cherrypy

class Sensors:
    exposed = True

    def GET(self, sensor_id=None):