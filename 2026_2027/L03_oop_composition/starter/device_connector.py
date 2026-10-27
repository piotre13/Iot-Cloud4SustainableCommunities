"""One room: the connector HAS sensors and an HVAC (composition). It only reads and forwards, no decisions."""


class DeviceConnector:
    def __init__(self, house_id, room_id, sensors, hvac):
        # TODO Ex5: store the four arguments, plus self.latest = {}
        self.house_id = house_id
        self.room_id = room_id
        self.unique_id = self.house_id + "/" + self.room_id
        self.sensors = sensors
        self.hvac = hvac
        self.latest = {}
        self.status_dict = {}
        # self.latest = []

    def read_sensors(self):
        for sens in self.sensors:
            # val_dict = {sens.name : sens.sense()}
            self.latest[sens.name] = sens.sense()

        return self.latest

        # raise NotImplementedError(
        #     "TODO Ex5: read every sensor, build {sensor.name: value}, save it in self.latest and return it"
        # )

    def actuate(self, command):
        self.hvac.actuate(command)

        # raise NotImplementedError("TODO Ex5: forward the command to the HVAC")

    def status(self):
        self.status_dict["house"] = self.house_id
        self.status_dict["room"] = self.room_id
        self.status_dict["latest"] = self.latest
        self.status_dict["HVAC_state"] = self.hvac.name
        return self.status_dict
        # raise NotImplementedError(
        #     "TODO Ex5: return a dict with house, room, latest and the HVAC state"
        # )
