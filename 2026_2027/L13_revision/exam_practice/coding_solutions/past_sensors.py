# Past exam style: fake sensors service. GET /sensors?type=temperature|light (both if omitted)
import sys
import random
import cherrypy


def bad(message):
    cherrypy.response.status = 400
    return {"error": message}


class FakeSensor:
    def __init__(self, name, unit, low, high, threshold, label):
        self.name = name
        self.unit = unit
        self.low = low
        self.high = high
        self.threshold = threshold
        self.label = label  # (adjective when above, adjective when below)

    def read(self):
        value = round(random.uniform(self.low, self.high), 1)
        adjective = self.label[0] if value > self.threshold else self.label[1]
        return {"type": self.name, "value": value, "unit": self.unit,
                "message": f"{self.name}: {value} {self.unit}, it is {adjective}!"}


class SensorsService:
    exposed = True

    def __init__(self):
        self.sensors = {
            "temperature": FakeSensor("temperature", "degrees", 0, 40, 30, ("too hot", "ok")),
            "light": FakeSensor("light", "lux", 0, 1000, 500, ("too bright", "too dark")),
        }

    def GET(self, *uri, **params):
        kind = params.get("type")
        if kind is None:
            chosen = list(self.sensors.values())
        elif kind in self.sensors:
            chosen = [self.sensors[kind]]
        else:
            return bad("type must be temperature or light")
        return {"readings": [s.read() for s in chosen]}


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    conf = {"/": {"request.dispatch": cherrypy.dispatch.MethodDispatcher(),
                  "tools.json_out.on": True}}
    cherrypy.tree.mount(SensorsService(), "/sensors", conf)
    cherrypy.config.update({"server.socket_port": port})
    cherrypy.engine.start()
    cherrypy.engine.block()
