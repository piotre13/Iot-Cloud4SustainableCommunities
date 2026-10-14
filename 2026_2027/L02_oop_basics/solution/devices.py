"""Sensors and the HVAC actuator of one room. No physics: the HVAC does not change the measurements."""
import random
from pathlib import Path

import pandas as pd  # only used by CsvSensor (Ex4)

# solution/ -> L02_oop_basics -> 2026_2027, where data/ lives
CSV_PATH = Path(__file__).parent.parent.parent / "data" / "meteo_frassinetto.csv"


# ---------- Ex1: base classes ----------
class Sensor:
    def __init__(self, name, unit):
        self.name = name
        self.unit = unit

    def sense(self):
        # "abstract" method: every child class must override it
        raise NotImplementedError("Sensor.sense() must be implemented by the child class")


class Actuator:
    def __init__(self, name):
        self.name = name

    def actuate(self, command):
        raise NotImplementedError("Actuator.actuate() must be implemented by the child class")


# ---------- Ex2: concrete sensors and actuator ----------
class RandomSensor(Sensor):
    def __init__(self, name, unit, low, high):
        super().__init__(name, unit)  # let the parent store name and unit
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


# ---------- Ex4 (extra): sensor that replays a real weather file ----------
class CsvSensor(Sensor):
    """Reads one column of the weather CSV, one row per call, starting again at the end."""

    def __init__(self, name, unit, column, path=CSV_PATH):
        super().__init__(name, unit)
        self.values = pd.read_csv(path)[column].tolist()
        self.index = 0

    def sense(self):
        value = self.values[self.index]
        self.index = (self.index + 1) % len(self.values)  # wrap around at the end
        return value
