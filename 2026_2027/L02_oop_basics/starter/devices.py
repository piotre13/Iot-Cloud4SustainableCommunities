"""Sensors and the HVAC actuator of one room. No physics: the HVAC does not change the measurements."""

import random
from pathlib import Path

import pandas as pd  # only used by CsvSensor (Ex4)

# starter/ -> L02_oop_basics -> 2026_2027, where data/ lives
CSV_PATH = Path(__file__).parent.parent.parent / "data" / "meteo_frassinetto.csv"


# ---------- Ex1: base classes ----------
class Sensor:
    def __init__(self, name, unit):
        self.name = name
        self.unit = unit

    def __repr__(self):
        return f"name:{self.name}, unit: {self.unit}"

    def sense(self):
        raise NotImplementedError(
            "TODO Ex1: raise NotImplementedError with a message (children must override sense)"
        )


class Actuator:
    def __init__(self, name):
        self.name = name

    def actuate(self, command):
        raise NotImplementedError(
            "TODO Ex1: raise NotImplementedError with a message (children must override actuate)"
        )


# ---------- Ex2: concrete sensors and actuator ----------
class RandomSensor(Sensor):
    def __init__(self, name, unit, low, high):
        super().__init__(name, unit)
        self.low = low
        self.high = high

    def sense(self):
        return round(random.uniform(self.low, self.high), 1)


class TemperatureSensor(RandomSensor):
    def __init__(self):
        super().__init__("temeprature", "Cel", 15, 28)


class HumiditySensor(RandomSensor):
    def __init__(self):
        super().__init__("humidity", "%", 0, 100)


class HVAC(Actuator):
    COMMANDS = ("ON", "OFF")

    def __init__(self):
        super().__init__("hvac")
        self.state = "OFF"

    def actuate(self, command):
        if command not in self.COMMANDS:
            raise ValueError("the comman is not available for this object!")
        else:
            self.state = command


# ---------- Ex4 (extra): sensor that replays a real weather file ----------
class CsvSensor(Sensor):
    """Reads one column of the weather CSV, one row per call, starting again at the end."""

    def __init__(self, name, unit, column, path=CSV_PATH):
        raise NotImplementedError(
            "TODO Ex4: call super().__init__, load pd.read_csv(path)[column].tolist(), index = 0"
        )

    def sense(self):
        raise NotImplementedError(
            "TODO Ex4: return the current value and move index on (back to 0 at the end)"
        )


if __name__ == "__main__":
    temp_sens = TemperatureSensor()

    sens_dict = {}
    for i in range(10):
        idx = f"temp_sens_{i}"
        sens_dict[idx] = TemperatureSensor()

    for k, val in sens_dict.items():
        print(k)
        print(val.name, val.unit, val.sense())
