"""One room: the connector HAS sensors and an HVAC (composition). It only reads and forwards, no decisions."""


class DeviceConnector:
    def __init__(self, house_id, room_id, sensors, hvac):
        # TODO Ex5: store the four arguments, plus self.latest = {}
        raise NotImplementedError("TODO Ex5: store house_id, room_id, sensors, hvac and an empty self.latest")

    def read_sensors(self):
        raise NotImplementedError("TODO Ex5: read every sensor, build {sensor.name: value}, save it in self.latest and return it")

    def actuate(self, command):
        raise NotImplementedError("TODO Ex5: forward the command to the HVAC")

    def status(self):
        raise NotImplementedError("TODO Ex5: return a dict with house, room, latest and the HVAC state")
