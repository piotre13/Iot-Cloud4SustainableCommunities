import cherrypy


class test:
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self, sensor_type=None):
        return sensor_type
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def run(self, sensor_type=None):

        return 'bella'


if __name__ == "__main__":
    conf = {
        "/": {
            "tools.sessions.on": True,
            "tools.response_headers.on": True,
            "tools.response_headers.headers": [("Content-Type", "application/json")],
        }
    }
    cherrypy.quickstart(test(), "/", conf)
