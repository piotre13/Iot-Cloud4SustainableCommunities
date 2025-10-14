from LightSensor import LightSensor
import time

class LightSensor1(LightSensor):
    def __init__(self, sensor_id, room=None):
        super().__init__(sensor_id, room)

    def run(self, simulation_steps=1, frequency=1):
        for _ in range(simulation_steps):
            time.sleep(frequency)
            self.sense()
        print("Simulation completed.")

if __name__ == "__main__":
    sensor = LightSensor1("LS1", "Living Room")
    sensor.run(simulation_steps=5, frequency=2)  # Simulate 5 readings with 2 seconds interval