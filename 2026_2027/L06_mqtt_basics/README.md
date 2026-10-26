# L07 - MQTT basics (3 h)

## Goals
- Understand publish/subscribe and how it differs from request/response (REST).
- Run a local broker and use topics, wildcards and QoS.
- Write publishers and subscribers with paho-mqtt v2.
- Build `MyMQTT`, the reusable class used by every smart-home service from now on.

## Theory (short)

**Request/response vs publish/subscribe.** With REST the client asks a server and waits for the answer: both must know each other. With MQTT nobody talks directly: publishers send messages to a **broker**, the broker forwards them to every **subscriber** interested in that topic. Publisher and subscriber do not know each other, and do not need to be online at the same time as each other (only the broker must be up).

**Topics** are strings with levels separated by `/`: `smarthome/house1/kitchen/temperature`. They are not created in advance: publishing on a topic is enough.

**Wildcards** (only in subscriptions, never when publishing):
- `+` replaces exactly one level: `smarthome/+/+/temperature` = temperature of every room of every house.
- `#` replaces everything below, only as the last level: `smarthome/house1/#` = all messages of house1.

**QoS** (delivery guarantee, between client and broker):
- 0: at most once (fire and forget)
- 1: at least once (acknowledged, a duplicate is possible)
- 2: exactly once (slowest)

The QoS actually used is the *lower* of the publisher's and the subscriber's.

**Retained message**: the broker keeps the last retained message of a topic and gives it immediately to every new subscriber.

**Clean session**: the broker forgets the client's subscriptions when it disconnects. Hence we **re-subscribe in `on_connect`**, which also covers reconnections after a broker restart.

**paho-mqtt v2 API**
```python
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="my_id")

def on_connect(client, userdata, flags, reason_code, properties): ...
def on_message(client, userdata, msg): ...   # msg.topic (str), msg.payload (bytes), msg.qos

client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883)
client.loop_start()      # network loop in a background thread
client.subscribe(topic, qos=1)
client.publish(topic, payload, qos=1)
client.loop_stop(); client.disconnect()
```
The payload is always bytes/string: for dictionaries we use `json.dumps` / `json.loads`.

## Install and run the broker (Mosquitto)
- macOS: `brew install mosquitto`. The broker binary is in `/opt/homebrew/sbin`: add it to the PATH (`export PATH=$PATH:/opt/homebrew/sbin`), or call it with the full path.
- Windows: download the installer from mosquitto.org.
- Linux: `sudo apt install mosquitto mosquitto-clients`.

Run it in its own terminal, in verbose mode, so you see every connection and message: `mosquitto -v` (default port 1883).

Quick tests without Python (two more terminals):
```
mosquitto_sub -t "smarthome/#" -v
mosquitto_pub -t smarthome/house1/kitchen/temperature -m 21.5
```
If you cannot install Mosquitto, `test.mosquitto.org` (port 1883) is a public broker you can use with `--broker test.mosquitto.org` (university networks may block it; anybody can read your messages, so use unique topics).

## Exercises
All scripts take `--broker` (default `localhost`) and `--port` (default `1883`), except Ex4 which takes `--broker host:port`. Work in `starter/`; `solution/` is for checking.

### Ex1 - plain publisher and subscriber
`ex1_publisher.py`: with a plain paho v2 client, publish a random temperature every 2 seconds on `--topic` (default `smarthome/house1/kitchen/temperature`).
`ex1_subscriber.py`: subscribe to `--topic` and print every message (topic and payload).

Run order: 1) `mosquitto -v` 2) `python ex1_subscriber.py` 3) `python ex1_publisher.py`.
Try: stop the subscriber and start it again - what did it miss? Start two subscribers.

### Ex2 - wildcards and QoS
`ex2_wildcards.py`: subscribe (with `--qos`) to `smarthome/+/+/temperature` and `smarthome/#`. For each message print the topic levels using `msg.topic.split("/")`, plus the qos of the delivered message.

Run two publishers for two rooms (change the topic) and compare:
```
python ex2_wildcards.py
python ex1_publisher.py --topic smarthome/house1/kitchen/temperature
python ex1_publisher.py --topic smarthome/house1/bedroom/temperature
```
Questions: why does every message arrive twice (once per filter)? Which filter would receive `smarthome/house1/alerts`? Publish with `mosquitto_pub -q 0` and `-q 2` and watch the qos printed.

### Ex3 - `MyMQTT`, a reusable class
`mymqtt.py`: class `MyMQTT(client_id, broker, port, notifier=None)` with `start()`, `stop()`, `publish(topic, payload_dict)`, `subscribe(topic)`, `unsubscribe(topic)`. Payloads are JSON. For each received message it calls `notifier.notify(topic, payload)` with `payload` already decoded to a dict. It remembers the subscribed topics and subscribes again in `on_connect`.

This is exactly the class in the final project (`smart_home/common/mymqtt.py`), with two fixes for typical bugs of the previous year's version:
1. `on_connect` iterates over `list(self.topics)`: `subscribe()` can be called from another thread and change the set while paho's thread is looping on it ("Set changed size during iteration").
2. `notifier.notify` is wrapped in `try/except`: an exception raised in a callback would kill paho's network loop and the client would silently stop receiving. Now the error is printed and the client keeps running. Non-JSON messages are ignored instead of crashing.

`ex3_demo.py`: a `Printer` class with `notify(topic, payload)` that prints what it receives, and a loop that publishes `{"value": ...}` every 2 s on `smarthome/house1/kitchen/temperature` while subscribed to `smarthome/house1/+/temperature`.

Note: Ex1 publishes plain numbers, which `MyMQTT` ignores (not JSON). Run `ex1_publisher.py` together with `ex3_demo.py` and see the difference.

### Ex4 - SenML sensors over MQTT
**SenML** (Sensor Measurement Lists) is a standard JSON format for sensor measurements. The form used in this course:
```
{"bn": "house1/kitchen", "bt": 1791970000, "e": [{"n": "temperature", "u": "Cel", "t": 0, "v": 21.4}]}
```
- `bn` base name: who measures (here `house/room`); `bt` base time: Unix time in seconds, valid for the whole message;
- `e` list of entries, one per measurement: `n` name, `u` unit (`Cel` = degrees Celsius, `%RH` = humidity), `t` time *relative* to `bt` (0 = now), `v` value.

(The IETF standard RFC 8428 has a slightly different JSON form, a plain array of records; the exams use the one above.)

`senml.py`: `senml_record(bn, n, u, v)` returns the dict above with one entry in `e` (`bt` = current Unix time, `t` = 0). A reader gets the value with `payload["e"][0]["v"]`.
`ex4_sensor_publisher.py house room [--interval 5] [--broker localhost:1883]`: using the random sensors of L02/L03 (`devices.py`), every N seconds publish one SenML record for temperature and one for humidity, on `smarthome/{house}/{room}/temperature` and `.../humidity`, through `MyMQTT`.

```
python ex4_sensor_publisher.py house1 kitchen --interval 2
python ex4_sensor_publisher.py house1 bedroom --interval 2
python ex2_wildcards.py        # watch both rooms
```

## Topics used by the smart home (from now on)
```
smarthome/{house}/{room}/temperature | humidity   SenML ({"bn","bt","e"})
smarthome/{house}/{room}/hvac                     {"command": "ON" | "OFF"}
smarthome/{house}/{room}/hvac/state               {"state": "ON" | "OFF"}
smarthome/{house}/alerts                          {"room": ..., "msg": ...}
```
