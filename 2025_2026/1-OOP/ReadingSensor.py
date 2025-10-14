import pandas as pd
from BaseSensor import Sensor
import time

class ReadingSensor(Sensor):
    def __init__(self, sensor_id, room=None, file_path=None):
        super().__init__(sensor_id, room)
        self.file_path = file_path
        if self.file_path:
            self.load_readings()
        else:
            raise ValueError("No file path provided!")

    def load_readings(self):
        self.readings = pd.read_csv(self.file_path)
        self.current_index = 0

    def sense(self, index):
        return self.readings.iloc[index] if 0 <= index < len(self.readings) else None

    def run(self, simulation_steps=1, frequency=1):
        for i in range(simulation_steps):
            time.sleep(frequency)
            reading = self.sense(i)
            if reading is not None:
                print(
                    f"Reading Sensor {self.sensor_id} in room {self.room} sensing value:\n{reading}"
                )
            else:
                print(f"No more readings available for sensor {self.sensor_id}.")
                break
        print("Simulation completed.")


if __name__ == "__main__":
    sensor = ReadingSensor(
        "RS1", room=None, file_path="2025_2026/1-OOP/meteo_frassinetto.csv"
    )
    print(sensor.readings.head())
    sensor.run(
        simulation_steps=5, frequency=2
    )  # Simulate 5 readings with 2 seconds interval
