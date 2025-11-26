import json
from copy import deepcopy
import cherrypy


class Catalog_utils:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load()

    def load(self):
        with open(self.file_path, "r") as f:
            data = json.load(f)
        return data

    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.data, f, indent=4)


class Catalog:
    exposed = True

    def __init__(self, catalog):
        self.catalog = catalog

    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        if len(uri) == 0:
            return self.catalog.data
        elif len(uri) == 1:
            if uri[0] in self.catalog.data.keys():
                return self.catalog.data[uri[0]]
            else:
                raise cherrypy.HTTPError(400)

        else:
            return "wrong uri"


class HousesCatalog:
    exposed = True

    def __init__(self, catalog):
        self.catalog = catalog

    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        if not params:
            dict_house = {"ids": []}
            for i in self.catalog.data["houses"]:
                dict_house["ids"].append(i["house_id"])
            return dict_house
        if params and "house_id" in params.keys():
            for i in self.catalog.data["houses"]:
                if i["house_id"] == params["house_id"]:
                    return i
                else:
                    raise cherrypy.HTTPError(400, message="House id not found!")
    
    @cherrypy.tools.json_in()
    def POST(self, *uri, **params):
        body = cherrypy.request.json
        house_id = 'house_%i'%len(self.catalog.data["houses"])
        new_house = deepcopy(body)
        new_house["house_id"] = house_id
        self.catalog.data["houses"].append(new_house)
        self.catalog.save()
        self.catalog.load()
        return {"house_id": house_id}

if __name__ == "__main__":
    catalog = Catalog_utils("2025_2026/2-REST/Catalog.json")
    conf = {
        "/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
            "tools.sessions.on": True,
        }
    }

    cherrypy.tree.mount(Catalog(catalog), "/project", conf)
    cherrypy.tree.mount(HousesCatalog(catalog), "/houses", conf)

    cherrypy.engine.start()
    cherrypy.engine.block()

    print("f")
