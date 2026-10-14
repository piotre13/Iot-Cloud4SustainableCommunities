"""Ex2 - calculator REST service.

Usage: python ex2_calculator.py [port]      (default 8080)

  GET  /add?a=1&b=2      (also sub, mul, div)
  POST /                 body: {"operation": "add", "operands": [1, 2, 3]}
"""
import sys

import cherrypy


def calculate(operation, operands):
    """Apply the operation left to right: [10, 2, 3] with 'sub' -> (10 - 2) - 3."""
    # hint: raise cherrypy.HTTPError(400, "...") for unknown operation, bad operands, division by zero
    raise NotImplementedError("TODO Ex2: validate the input and compute the result")


class Calculator:
    exposed = True

    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        # hint: wrong path -> 404, missing a or b -> 400, then use calculate()
        raise NotImplementedError("TODO Ex2: GET /<operation>?a=..&b=.. -> JSON")

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self, *uri, **params):
        # hint: the parsed body is in cherrypy.request.json
        raise NotImplementedError("TODO Ex2: POST / with {operation, operands} -> JSON")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    conf = {"/": {"request.dispatch": cherrypy.dispatch.MethodDispatcher()}}
    cherrypy.config.update({"server.socket_port": port})
    cherrypy.tree.mount(Calculator(), "/", conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
