import random

class Sensor:
    def __init__(self, sensor_id, sensor_type, room=None):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.room = room
        print(f"Sensor {self.sensor_id} of type {self.sensor_type} initialized.")

    def register(self):
        print(f"Registering Sensor {self.sensor_id} in room {self.room}")

    def sense(self):
        val = random.randint(0, 100)  # Simulated sensor value
        print(f"Sensing value from Sensor {self.sensor_id}: {val}")
        return val