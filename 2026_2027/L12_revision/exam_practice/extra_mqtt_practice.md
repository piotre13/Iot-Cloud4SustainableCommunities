# Extra practice - MQTT (not asked in the coding part of past exams)

Real exams so far ask for a REST web service in the coding question. This exercise is only extra practice for MQTT.

## Task: room-average alert
Write a Python program, object-oriented, using paho-mqtt (v2) that:
1. subscribes with ONE wildcard topic to the temperature of every room of every house: `smarthome/+/+/temperature`;
2. each message is a SenML record such as `{"bn": "house1/kitchen", "bt": 1791970000, "e": [{"n": "temperature", "u": "Cel", "t": 0, "v": 27}]}`;
3. keeps, per house and room, the last 3 values and computes their average;
4. when the average is above a threshold (default 26), publishes on `smarthome/<house>/alerts` the JSON `{"room": "kitchen", "msg": "average temperature 27.3 above 26.0"}` with QoS 1;
5. ignores malformed messages without crashing;
6. broker host, port, threshold and window size are optional command-line arguments.

Questions to answer too: which QoS did you choose for the subscription and why? What happens to the subscription when the connection drops and you reconnect?

## Try it
```
/opt/homebrew/sbin/mosquitto -p 1890                      # terminal 1 (own broker)
python coding_solutions/extra_mqtt.py localhost 1890      # terminal 2
mosquitto_sub -p 1890 -t 'smarthome/+/alerts'             # terminal 3
mosquitto_pub -p 1890 -t smarthome/house1/kitchen/temperature -m '{"bn":"house1/kitchen","bt":1791970000,"e":[{"n":"temperature","u":"Cel","t":0,"v":30}]}'
```
Hints: subscribe inside `on_connect` (so it is renewed after a reconnect); catch errors inside `on_message`, an exception there would stop the network loop.
Solution: `coding_solutions/extra_mqtt.py`.
