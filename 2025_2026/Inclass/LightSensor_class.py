from Inclass.BaseSensor_class import BaseSensor
from datetime import datetime
import random

class LightSensor(BaseSensor):
    def __init__(self, sensor_id, room=None):
        super().__init__(sensor_id, "Light", room)

    def sense(self):
        hour = datetime.now().hour
        if 6 <= hour < 10:
            val = random.randint(20, 80)
        elif 10<= hour < 16:
            val = random.randint(80, 120)
        elif 16 <= hour <20:
            val = random.randint(20, 80)
        else:
            val = random.randint(0, 10)
        
        print('[SENSOR] LightSensor {} in room {} sensed value: {}'.format(self.id, self.room, val))
        return val


        



if __name__ == "__main__":
    sensor = LightSensor("LS-001", "Living Room")
    sensor.sense()
