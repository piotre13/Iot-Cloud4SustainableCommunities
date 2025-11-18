import cherrypy


class Calculator_service:
    exposed = True

    def __init__(self):
        pass

    def add(self, a, b):
        return a + b

    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        if len(uri) > 0 and params != {} and "a" in params and "b" in params:
            a = float(params["a"])
            b = float(params["b"])

            if uri[0] == "sum":
                res = self.add(a, b)
                return_dict = {"operation": "sum", "result": res}
                return return_dict

            elif uri[0] == "multiply":
                pass
            elif uri[0] == "divide":
                pass
            elif uri[0] == "subtract":
                pass

        return "sorry you have to specify a operation"


if __name__ == "__main__":
    conf = {
        "/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
            "tools.sessions.on": True,
        }
    }

    cherrypy.tree.mount(Calculator_service(), "/", conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
