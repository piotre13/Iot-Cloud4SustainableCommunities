# Practice only: per-room average + alert publisher.
# Subscribes to smarthome/+/+/temperature (SenML), keeps the last N values per room,
# publishes an alert on smarthome/<house>/alerts when the average exceeds the threshold.
# Run: python extra_mqtt.py [broker_host] [broker_port] [threshold] [window]
import sys
import json
import paho.mqtt.client as mqtt


class RoomAverager:
    def __init__(self, threshold, window):
        self.threshold = threshold
        self.window = window
        self.values = {}  # (house, room) -> last values

    def add(self, house, room, value):
        """Store a value, return the average of the last `window` values."""
        values = self.values.setdefault((house, room), [])
        values.append(value)
        del values[:-self.window]
        return sum(values) / len(values)


class AlertService:
    def __init__(self, host, port, threshold, window):
        self.averager = RoomAverager(threshold, window)
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="extra_mqtt_averager")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.host = host
        self.port = port

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print("connected:", reason_code)
        client.subscribe("smarthome/+/+/temperature", qos=1)  # re-subscribe on every reconnect

    def on_message(self, client, userdata, msg):
        try:
            _, house, room, _ = msg.topic.split("/")
            value = json.loads(msg.payload)["e"][0]["v"]
            average = self.averager.add(house, room, float(value))
        except (ValueError, KeyError, TypeError):
            print("ignored bad message on", msg.topic)  # an exception here would kill the network loop
            return
        print(f"{house}/{room} average = {average:.1f}")
        if average > self.averager.threshold:
            alert = {"room": room, "msg": f"average temperature {average:.1f} above {self.averager.threshold}"}
            client.publish(f"smarthome/{house}/alerts", json.dumps(alert), qos=1)

    def run(self):
        self.client.connect(self.host, self.port)
        self.client.loop_forever()


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 1883
    threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 26
    window = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    AlertService(host, port, threshold, window).run()
