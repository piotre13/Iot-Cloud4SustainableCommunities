# L01 - Intro, environment, Python refresh, course project

Duration: 1.5 h

## Goals
- Set up the Python environment (venv + VS Code).
- Refresh Python: functions, dicts, lists, loops, reading/writing JSON.
- Know what we will build during the course.
- Produce `config.json`, reused in later lessons (L03 loads the rooms from it).

## The course project
We build, lesson by lesson, a **smart home** system. Each room has a
temperature/humidity sensor and an ON/OFF HVAC (heating/cooling). The system must
scale to many houses.

It is made of small independent **microservices**: a catalog, device connectors,
a controller, a ThingSpeak adaptor and a Telegram bot. They talk to each other
only through **REST** and **MQTT**.


## Environment setup
Python 3.12 is required. From the folder `2026_2027/`:

```bash
python3.12 -m venv .venv
# activate: macOS / Linux
source .venv/bin/activate
# activate: Windows (PowerShell)
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python --version      # must say 3.12.x
```

VS Code: `Cmd/Ctrl+Shift+P` -> "Python: Select Interpreter" -> choose the one
inside `.venv`. Open a new terminal: the prompt should start with `(.venv)`.

## Short theory
- A **function** (`def`) groups code we want to reuse; `return` gives a value back.
- JSON maps to Python types: object -> `dict`, array -> `list`, number -> `int`/`float`.
- `json.load(f)` reads a file into Python; `json.dump(obj, f, indent=2)` writes it.
- `Path(__file__).parent` is the folder of the current script, so file paths work
  from any working directory.
- dicts and lists are **mutable**: changing one through a second name changes both.

## How to run
Work in `starter/`, compare with `solution/`. Run from inside the folder:

```bash
cd starter      # or solution
python ex1_functions.py
```
Until you implement a function you will see `NotImplementedError: TODO ...`.

## Exercises

### Ex1 - functions (`ex1_functions.py`)
Implement `celsius_to_fahrenheit(c)`, `is_too_cold(temp, t_min)`,
`is_too_hot(temp, t_max)` and `hvac_command(temp, t_min, t_max)`, which returns
`"ON"` (too cold: switch the heating on), `"OFF"` (too hot) or `None` (inside the band:
leave the HVAC as it is). This is the same rule the project's controller uses.
Run the file and check the printed results.

### Ex2 - read the configuration (`ex2_config.py`, `config.json`)
Look at `config.json` (houses -> rooms -> thresholds). Implement:
- `load_config(path)`: read the JSON file and return the dict.
- `list_rooms(config)`: return strings like `"house1/kitchen"`.
- `get_thresholds(config, house_id, room_id)`: return the thresholds dict, or
  `None` if the house or room does not exist.

### Ex3 - modify and save (`ex3_save.py`)
Change a threshold in the loaded dict and implement `save_config(config, path)`
with `json.dump(config, f, indent=2)`. Save to a NEW file `config_modified.json`:
never overwrite `config.json`. (Ex3 uses the functions of Ex2.)
