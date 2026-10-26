"""Sensors and the HVAC actuator of one room. No physics: the HVAC does not change the measurements."""
import random
from pathlib import Path

import pandas as pd

CSV_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "meteo_frassinetto.csv"


class Sensor:
    def __init__(self, name, unit):
        self.name = name
        self.unit = unit

    def sense(self):
        raise NotImplementedError


class RandomSensor(Sensor):
    def __init__(self, name, unit, low, high):
        super().__init__(name, unit)
        self.low = low
        self.high = high

    def sense(self):
        return round(random.uniform(self.low, self.high), 1)


class TemperatureSensor(RandomSensor):
    def __init__(self):
        super().__init__("temperature", "Cel", 15, 28)


class HumiditySensor(RandomSensor):
    def __init__(self):
        super().__init__("humidity", "%RH", 40, 80)


class CsvSensor(Sensor):
    """Reads one column of the weather CSV, one row per call, starting again at the end."""

    def __init__(self, name, unit, column, path=CSV_PATH):
        super().__init__(name, unit)
        self.values = pd.read_csv(path)[column].tolist()
        self.index = 0

    def sense(self):
        value = self.values[self.index]
        self.index = (self.index + 1) % len(self.values)
        return value


def make_sensors(source):
    if source == "csv":
        return [CsvSensor("temperature", "Cel", "DryBulb"), CsvSensor("humidity", "%RH", "RelHum")]
    return [TemperatureSensor(), HumiditySensor()]


class Actuator:
    def __init__(self, name):
        self.name = name

    def actuate(self, command):
        raise NotImplementedError


class HVAC(Actuator):
    COMMANDS = ("ON", "OFF")

    def __init__(self):
        super().__init__("hvac")
        self.state = "OFF"

    def actuate(self, command):
        if command not in self.COMMANDS:
            raise ValueError(f"Unknown command {command!r}, expected one of {self.COMMANDS}")
        self.state = command
        print(f"HVAC -> {self.state}")
