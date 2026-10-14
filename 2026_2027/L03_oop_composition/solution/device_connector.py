"""One room: the connector HAS sensors and an HVAC (composition). It only reads and forwards, no decisions."""


class DeviceConnector:
    def __init__(self, house_id, room_id, sensors, hvac):
        self.house_id = house_id
        self.room_id = room_id
        self.sensors = sensors
        self.hvac = hvac
        self.latest = {}

    def read_sensors(self):
        self.latest = {sensor.name: sensor.sense() for sensor in self.sensors}
        return self.latest

    def actuate(self, command):
        self.hvac.actuate(command)

    def status(self):
        return {
            "house": self.house_id,
            "room": self.room_id,
            "latest": self.latest,
            "hvac": self.hvac.state,
        }
