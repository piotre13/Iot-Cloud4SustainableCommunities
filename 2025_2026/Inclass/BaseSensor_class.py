import random

class BaseSensor:
    def __init__(self, id, sensor_type, room=None):
        self.id = id
        self.sensor_type = sensor_type
        self.room = room
        print(f"Sensor {self.id} of type {self.sensor_type} initialized in room: {self.room}")
        self.register()

    def register(self):
        print(f"Registering sensor {self.id} of type {self.sensor_type} in room: {self.room}")

    def sense(self):
        val = random.random() * 100
        print(f"Sensor {self.id} sensing value: {val:.2f}")
        return val
        

if __name__ == "__main__":
    # Simple test
    sensor = BaseSensor("S-001", "Light", "Living Room")
    sensor.sense()

    sensor2 = BaseSensor("S-002", "Temperature")
    sensor2.sense()

    sensor3 = BaseSensor("S-003", "Humidity", "Kitchen")
    sensor3.sense()