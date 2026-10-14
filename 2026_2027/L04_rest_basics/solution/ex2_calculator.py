"""Ex2 - calculator REST service.

Usage: python ex2_calculator.py [port]      (default 8080)

  GET  /add?a=1&b=2      (also sub, mul, div)
  POST /                 body: {"operation": "add", "operands": [1, 2, 3]}
"""
import sys

import cherrypy


def calculate(operation, operands):
    """Apply the operation left to right: [10, 2, 3] with 'sub' -> (10 - 2) - 3."""
    if operation not in ("add", "sub", "mul", "div"):
        raise cherrypy.HTTPError(400, f"Unknown operation '{operation}'")
    if not isinstance(operands, list) or len(operands) < 2:
        raise cherrypy.HTTPError(400, "operands must be a list with at least 2 numbers")
    try:
        numbers = [float(x) for x in operands]
    except (TypeError, ValueError):
        raise cherrypy.HTTPError(400, "operands must be numbers")

    result = numbers[0]
    for x in numbers[1:]:
        if operation == "add":
            result += x
        elif operation == "sub":
            result -= x
        elif operation == "mul":
            result *= x
        else:
            if x == 0:
                raise cherrypy.HTTPError(400, "Division by zero")
            result /= x
    return result


class Calculator:
    exposed = True

    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        if len(uri) != 1 or uri[0] not in ("add", "sub", "mul", "div"):
            raise cherrypy.HTTPError(404, "Use /add, /sub, /mul or /div")
        for name in ("a", "b"):
            if name not in params:
                raise cherrypy.HTTPError(400, f"Missing parameter '{name}'")
        # calculate() also checks that a and b are numbers
        result = calculate(uri[0], [params["a"], params["b"]])
        return {"operation": uri[0], "a": float(params["a"]), "b": float(params["b"]),
                "result": result}

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self, *uri, **params):
        if len(uri) != 0:
            raise cherrypy.HTTPError(404, "POST goes to /")
        body = cherrypy.request.json  # already parsed; invalid JSON -> 400 by CherryPy
        if not isinstance(body, dict) or "operation" not in body or "operands" not in body:
            raise cherrypy.HTTPError(400, "Body must have 'operation' and 'operands'")
        result = calculate(body["operation"], body["operands"])
        return {"operation": body["operation"],
                "operands": [float(x) for x in body["operands"]],
                "result": result}


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    conf = {"/": {"request.dispatch": cherrypy.dispatch.MethodDispatcher()}}
    cherrypy.config.update({"server.socket_port": port})
    cherrypy.tree.mount(Calculator(), "/", conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
