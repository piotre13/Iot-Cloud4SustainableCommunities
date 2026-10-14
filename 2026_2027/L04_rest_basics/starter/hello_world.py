"""HelloWorld - minimal CherryPy server.

Usage: python hello_world.py [port]      (default 8080)
Try:   http://localhost:8080/            http://localhost:8080/?name=Anna
"""
import sys

import cherrypy


class HelloWorld:
    exposed = True  # required by MethodDispatcher

    def GET(self, *uri, **params):
        # hint: if "name" is in params greet that name, otherwise return "Hello World"
        raise NotImplementedError("TODO HelloWorld: return 'Hello World' or 'Hello <name>'")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    conf = {"/": {"request.dispatch": cherrypy.dispatch.MethodDispatcher()}}
    cherrypy.config.update({"server.socket_port": port})
    cherrypy.tree.mount(HelloWorld(), "/", conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
