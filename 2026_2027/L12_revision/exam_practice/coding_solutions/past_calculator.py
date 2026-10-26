# Past exam style: calculator. GET /calculator/<sum|difference|multiplication|division>?operand_1=5&operand_2=25
import sys
import cherrypy


def bad(message):
    cherrypy.response.status = 400
    return {"error": message}


class Calculator:
    def compute(self, operation, a, b):
        if operation == "sum":
            return a + b
        if operation == "difference":
            return a - b
        if operation == "multiplication":
            return a * b
        if operation == "division":
            return a / b
        raise KeyError(operation)


class CalculatorService:
    exposed = True

    def __init__(self):
        self.calculator = Calculator()

    def GET(self, *uri, **params):
        if len(uri) != 1:
            return bad("use /calculator/<operation>?operand_1=..&operand_2=..")
        operation = uri[0]
        try:
            a = float(params["operand_1"])
            b = float(params["operand_2"])
        except KeyError:
            return bad("operand_1 and operand_2 are required")
        except ValueError:
            return bad("operands must be numbers")
        try:
            result = self.calculator.compute(operation, a, b)
        except KeyError:
            return bad("unknown operation")
        except ZeroDivisionError:
            return bad("division by zero")
        # show integers as integers (5, not 5.0)
        a, b, result = [int(x) if x == int(x) else x for x in (a, b, result)]
        return {"operand_1": a, "operand_2": b, "operation": operation, "result": result}


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    conf = {"/": {"request.dispatch": cherrypy.dispatch.MethodDispatcher(),
                  "tools.json_out.on": True}}
    cherrypy.tree.mount(CalculatorService(), "/calculator", conf)
    cherrypy.config.update({"server.socket_port": port})
    cherrypy.engine.start()
    cherrypy.engine.block()
