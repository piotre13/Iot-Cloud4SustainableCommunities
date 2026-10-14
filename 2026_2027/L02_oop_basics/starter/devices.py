"""Sensors and the HVAC actuator of one room. No physics: the HVAC does not change the measurements."""
import random
from pathlib import Path

import pandas as pd  # only used by CsvSensor (Ex4)

# starter/ -> L02_oop_basics -> 2026_2027, where data/ lives
CSV_PATH = Path(__file__).parent.parent.parent / "data" / "meteo_frassinetto.csv"


# ---------- Ex1: base classes ----------
class Sensor:
    def __init__(self, name, unit):
        raise NotImplementedError("TODO Ex1: store name and unit as attributes")

    def sense(self):
        raise NotImplementedError("TODO Ex1: raise NotImplementedError with a message (children must override sense)")


class Actuator:
    def __init__(self, name):
        raise NotImplementedError("TODO Ex1: store name as attribute")

    def actuate(self, command):
        raise NotImplementedError("TODO Ex1: raise NotImplementedError with a message (children must override actuate)")


# ---------- Ex2: concrete sensors and actuator ----------
class RandomSensor(Sensor):
    def __init__(self, name, unit, low, high):
        raise NotImplementedError("TODO Ex2: call super().__init__ and store low and high")

    def sense(self):
        raise NotImplementedError("TODO Ex2: return round(random.uniform(low, high), 1)")


class TemperatureSensor(RandomSensor):
    def __init__(self):
        raise NotImplementedError('TODO Ex2: call super().__init__("temperature", "Cel", 15, 28)')


class HumiditySensor(RandomSensor):
    def __init__(self):
        raise NotImplementedError('TODO Ex2: call super().__init__("humidity", "%RH", 40, 80)')


class HVAC(Actuator):
    COMMANDS = ("ON", "OFF")

    def __init__(self):
        raise NotImplementedError('TODO Ex2: call super().__init__("hvac") and set state to "OFF"')

    def actuate(self, command):
        raise NotImplementedError("TODO Ex2: ValueError if command not in COMMANDS, else store it and print 'HVAC -> ON'")


# ---------- Ex4 (extra): sensor that replays a real weather file ----------
class CsvSensor(Sensor):
    """Reads one column of the weather CSV, one row per call, starting again at the end."""

    def __init__(self, name, unit, column, path=CSV_PATH):
        raise NotImplementedError("TODO Ex4: call super().__init__, load pd.read_csv(path)[column].tolist(), index = 0")

    def sense(self):
        raise NotImplementedError("TODO Ex4: return the current value and move index on (back to 0 at the end)")
