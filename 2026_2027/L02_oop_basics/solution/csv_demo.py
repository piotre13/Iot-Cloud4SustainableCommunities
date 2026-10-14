# Ex4 (extra): same loop as main.py, but the values come from a real weather file
from devices import CsvSensor

sensors = [CsvSensor("temperature", "Cel", "DryBulb"), CsvSensor("humidity", "%RH", "RelHum")]

for _ in range(5):
    for sensor in sensors:
        print(f"{sensor.name}: {sensor.sense()} {sensor.unit}")
