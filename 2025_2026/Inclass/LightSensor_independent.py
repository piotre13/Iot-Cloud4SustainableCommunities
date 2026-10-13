from Inclass.LightSensor_ex import LightSensor
import time
class LightSensor_independent(LightSensor):
    def __init__(self, sensor_id, room):
        super().__init__(sensor_id, room)   
    

    def run(self, steps, frequency):

        for _ in range(steps):
            self.sense()
            time.sleep(frequency)

if __name__ == "__main__":

    sensor = LightSensor_independent("LS-001", "LivingRoom")
    sensor.run(130, 4)  # Run for 5 steps with a frequency of 2 seconds
