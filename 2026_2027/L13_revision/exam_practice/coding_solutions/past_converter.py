# Past exam style: unit converter. GET /convert/<conversion>?value=100
import sys
import cherrypy


def bad(message):
    cherrypy.response.status = 400
    return {"error": message}


class Converter:
    CONVERSIONS = {
        "kilometers_to_miles": lambda v: v * 0.6213,
        "miles_to_kilometers": lambda v: v * 1.6093,
        "celsius_to_fahrenheit": lambda v: v * 9 / 5 + 32,
        "fahrenheit_to_celsius": lambda v: (v - 32) * 5 / 9,
    }

    def convert(self, conversion, value):
        return round(self.CONVERSIONS[conversion](value), 2)


class ConverterService:
    exposed = True

    def __init__(self):
        self.converter = Converter()

    def GET(self, *uri, **params):
        if len(uri) != 1 or uri[0] not in Converter.CONVERSIONS:
            return bad("use /convert/<" + "|".join(Converter.CONVERSIONS) + ">?value=..")
        try:
            value = float(params["value"])
        except KeyError:
            return bad("value is required")
        except ValueError:
            return bad("value must be a number")
        if value == int(value):
            value = int(value)
        return {"input_value": value, "conversion": uri[0],
                "result": self.converter.convert(uri[0], value)}


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    conf = {"/": {"request.dispatch": cherrypy.dispatch.MethodDispatcher(),
                  "tools.json_out.on": True}}
    cherrypy.tree.mount(ConverterService(), "/convert", conf)
    cherrypy.config.update({"server.socket_port": port})
    cherrypy.engine.start()
    cherrypy.engine.block()
