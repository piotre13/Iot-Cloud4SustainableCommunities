# Mock exam coding question: room comfort service.
# Run: python mock_coding.py [port]      Try: curl "http://localhost:8080/comfort?temperature=28&humidity=45"
import sys
import cherrypy


def bad(message):
    # one place for all errors: 400 + JSON body
    cherrypy.response.status = 400
    return {"error": message}


class ComfortEvaluator:
    """Business logic, separated from HTTP."""
    T_MIN = 18
    T_MAX = 26
    H_MAX = 60

    def evaluate(self, temperature, humidity):
        if temperature < self.T_MIN:
            comfort = "too_cold"
        elif temperature > self.T_MAX:
            comfort = "too_hot"
        elif humidity > self.H_MAX:
            comfort = "too_humid"
        else:
            comfort = "comfortable"
        command = "ON" if comfort == "too_cold" else "OFF"  # the HVAC is a heater
        return {"temperature": temperature, "humidity": humidity,
                "comfort": comfort, "hvac_command": command}


class ComfortService:
    exposed = True

    def __init__(self):
        self.evaluator = ComfortEvaluator()

    def GET(self, *uri, **params):
        # GET because it is a read-only computation: safe, no state is changed
        if uri:
            return bad("use /comfort?temperature=..&humidity=..")
        try:
            temperature = float(params["temperature"])
            humidity = float(params["humidity"])
        except KeyError:
            return bad("temperature and humidity are required")
        except ValueError:
            return bad("temperature and humidity must be numbers")
        if not 0 <= humidity <= 100:
            return bad("humidity must be in [0, 100]")
        return self.evaluator.evaluate(temperature, humidity)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    conf = {"/": {"request.dispatch": cherrypy.dispatch.MethodDispatcher(),
                  "tools.json_out.on": True}}
    cherrypy.tree.mount(ComfortService(), "/comfort", conf)
    cherrypy.config.update({"server.socket_port": port})
    cherrypy.engine.start()
    cherrypy.engine.block()
