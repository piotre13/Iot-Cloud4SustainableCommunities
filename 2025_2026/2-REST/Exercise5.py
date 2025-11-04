import os

import cherrypy


class Plugin:
    exposed = True

    def __init__(self):
        self.id = 1

    def GET(self):
        path = os.path.join(os.path.dirname(__file__), "index.html")
        return open(path)


if __name__ == "__main__":
   
    config = {
        "/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
            "tools.staticdir.root": os.path.abspath(os.path.dirname(__file__)),
        },
        "/css": {"tools.staticdir.on": True, "tools.staticdir.dir": "./css"},
        "/js": {"tools.staticdir.on": True, "tools.staticdir.dir": "./js"},
    }

    cherrypy.tree.mount(Plugin(), "/", config)
    cherrypy.engine.start()
    cherrypy.engine.block()
