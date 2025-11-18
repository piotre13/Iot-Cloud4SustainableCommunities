import cherrypy


class Sum:
    exposed = True

    def GET(self, *uri, **params):
        if params:
            a = params.get("a", 4)
            b = params.get("b", 4)
            res = float(a) + float(b)
            return str(res)
    
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self, *uri,**params):
        print(params)
        body =  cherrypy.request.json
        res = 0
        for k, val in body.items():
            res+=float(val)
        
        return {'res':res}

class Diff:
    exposed = True

    def GET(self, *uri, **params):
        if params:
            a = params.get("a", 4)
            b = params.get("b", 4)
            res = float(a) - float(b)
            return str(res)


class Mult:
    exposed = True

    def GET(self, *uri, **params):
        if params:
            a = params.get("a", 4)
            b = params.get("b", 4)
            res = float(a) * float(b)
            return str(res)


class Div:
    exposed = True

    def GET(self, *uri, **params):
        if params:
            a = params.get("a", 4)
            b = params.get("b", 4)
            if b != 0:
                res = float(a) / float(b)
            else:
                res = "Division to 0 noit allowed"
            return str(res)


if __name__ == "__main__":
    conf = {
        "/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
            "tools.sessions.on": True,
        }
    }

    cherrypy.tree.mount(Sum(), "/sum", conf)
    cherrypy.tree.mount(Diff(), "/diff", conf)
    cherrypy.tree.mount(Mult(), "/mult", conf)
    cherrypy.tree.mount(Div(), "/div", conf)

    cherrypy.engine.start()
    cherrypy.engine.block()
