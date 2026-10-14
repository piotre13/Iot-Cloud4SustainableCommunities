# L02 - OOP 1: classes, inheritance, polymorphism

Duration: 3 h. Domain: one smart-home room with a temperature sensor, a humidity sensor and an ON/OFF HVAC.
There is no physics: sensors return random values and the HVAC does not change them.

## Goals
- Write a class with `__init__` and methods.
- Reuse code with inheritance and `super()`.
- Use polymorphism: one call (`sense()`), many kinds of sensor.
- Mark a method as "to be implemented by the child" with `NotImplementedError`.

The classes written here (`Sensor`, `RandomSensor`, `TemperatureSensor`, `HumiditySensor`, `CsvSensor`, `Actuator`, `HVAC`)
are the same ones used later in `smart_home/device_connector/devices.py`.

## Theory in short
- **Class**: a blueprint. **Object**: one instance built from it, e.g. `t = TemperatureSensor()`.
- **`__init__`**: runs when the object is created; it sets the initial attributes.
- **`self`**: the object itself. `self.name = name` stores data inside the object.
- **Inheritance**: `class RandomSensor(Sensor)` gets everything `Sensor` has and adds or changes things.
- **`super()`**: calls the parent class, usually `super().__init__(...)` to let the parent set its attributes.
- **Polymorphism**: objects of different classes answer the same method call in their own way:
  ```python
  for sensor in [TemperatureSensor(), HumiditySensor()]:
      print(sensor.sense())
  ```
- **"Abstract" method**: the parent declares it and raises `NotImplementedError`; every child must override it.

## Folders
- `starter/`: skeletons with `raise NotImplementedError("TODO ...")`. Work here.
- `solution/`: complete code, to compare with yours.

## Exercises

### Ex1 - Base classes (`devices.py`)
- `Sensor(name, unit)`: stores `name` and `unit`; `sense()` raises `NotImplementedError`.
- `Actuator(name)`: stores `name`; `actuate(command)` raises `NotImplementedError`.

Check: `Sensor("x", "u").sense()` must fail with `NotImplementedError`.

### Ex2 - Concrete devices (`devices.py`)
- `RandomSensor(Sensor)` with `low` and `high`; `sense()` returns `round(random.uniform(low, high), 1)`.
- `TemperatureSensor()` is a `RandomSensor("temperature", "Cel", 15, 28)`.
- `HumiditySensor()` is a `RandomSensor("humidity", "%RH", 40, 80)`.
- `HVAC(Actuator)`: `state` starts as `"OFF"`. `actuate(command)` accepts only `"ON"` or `"OFF"`
  (otherwise `ValueError`), stores the state and prints `HVAC -> ON`.
- Polymorphism: put both sensors in a list and call `sense()` on each in a loop.

### Ex3 - Command line (`main.py`)
Loop with a menu read through `input()`:

```
1) read sensors
2) HVAC ON
3) HVAC OFF
q) quit
```
Any other input prints an "invalid choice" message and the menu is shown again.

### Ex4 (extra, optional) - Sensor from a CSV file (`devices.py`, `csv_demo.py`)
`CsvSensor(Sensor)` reads one column of the weather file with `pd.read_csv(path)[column].tolist()`.
Each `sense()` returns the next row and starts again from the first one at the end.
Temperature column: `DryBulb` (Celsius). Humidity column: `RelHum` (%).
The file is `2026_2027/data/meteo_frassinetto.csv` (do not copy it; `CSV_PATH` already points to it).
In `csv_demo.py` print 5 readings of each sensor. The first temperature must be `-1.68`.

Notice that `CsvSensor` is used exactly like `TemperatureSensor`: this is the point of polymorphism.

## How to run
From the repository root, with the course virtual environment active (pandas is needed only for Ex4):

```
cd 2026_2027/L02_oop_basics/solution     # or starter/
python main.py
python csv_demo.py                        # Ex4
```
The starter fails with `NotImplementedError: TODO ...` until you fill in the exercise it names.
