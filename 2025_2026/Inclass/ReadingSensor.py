import pandas as pd
import time

class Sensor:
    def __init__(self, sensor_id, file_path, room=None):
        self.sensor_id = sensor_id
        self.room = room
        self.type = "Weather-Temperature"
        self.data = pd.read_csv(file_path).DryBulb

    def sense(self, i):
        return self.data.values[i]
      

    def run(self, ts, frequency):
        for i in range(ts):
            val =self.sense(i)
            print(f"at iteration, {i} sensed value:{val}")
            time.sleep(frequency)
        


if __name__ == "__main__":
    sensor = Sensor(
        "S1", file_path="2025_2026/1-OOP/meteo_frassinetto.csv", room="Living Room"
    )
    print(sensor.data.head())
    sensor.run(ts=10, frequency=1)  # Simulate 5 readings with 2 seconds interval
