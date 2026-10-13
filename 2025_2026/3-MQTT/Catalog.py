import cherrypy


class Catalog:
    exposed = True

    def __init__(self):
        self.data = {
            "broker": "localhost",
            "port": 1883,
            "base_topic": "house1",
            "thresholds": [
                {"room": "kitchen", "val": 20000},
                {"room": "living_room", "val": 300},
            ],
            "rooms": [{"room_name": "kitchen", "sensors": [], "actuators": []}],
        }

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self, *uri, **params):
        data = cherrypy.request.json
        print(data)
        for room in self.data["rooms"]:
            if room["room_name"] == data["room_name"]:
                if data["type"] == "sensor" and len(room["sensors"]) == 0:
                    sens_id = f"{room['room_name']}_sens{len(room['sensors'])}"
                    topic = (
                        self.data["base_topic"]
                        + "/"
                        + room["room_name"]
                        + "/"
                        + "sens_%i" % len(room["sensors"])
                    )
                    room["sensors"].append({"sens_name": sens_id, "topic": topic})
                    answer = {
                        "broker": self.data["broker"],
                        "port": self.data["port"],
                        "topic": topic,
                        "unique_id": sens_id,
                    }
                    return answer

                if data["type"] == "actuator" and len(room["actuators"]) == 0:
                    act_id = f"{room['room_name']}_act{len(room['actuators'])}"
                    topic = (
                        self.data["base_topic"]
                        + "/"
                        + room["room_name"]
                        + "/"
                        + "act_%i" % len(room["actuators"])
                    )
                    room["actuators"].append({"act_name": act_id, "topic": topic})
                    answer = {
                        "broker": self.data["broker"],
                        "port": self.data["port"],
                        "topic": topic,
                        "unique_id": act_id,
                    }
                    return answer

    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        if len(uri) > 0:
            if uri[0] == "thresholds":
                answer = {}
                for room in self.data["rooms"]:
                    for sens in room["sensors"]:
                        if sens["topic"] not in answer.keys():
                            th = None
                            for r in self.data["thresholds"]:
                                if r["room"] == room["room_name"]:
                                    th = r["val"]
                            if th:
                                answer[sens["topic"]] = th
                return answer
            if uri[0] == "pairs":
                answer = {}
                for room in self.data["rooms"]:
                    answer[room["sensors"][0]["topic"]] = room["actuators"][0][
                        "topic"
                    ]

                return answer


if __name__ == "__main__":
    conf = {
        "/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
            "tools.sessions.on": True,
        }
    }

    cherrypy.tree.mount(Catalog(), "/house1", conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
