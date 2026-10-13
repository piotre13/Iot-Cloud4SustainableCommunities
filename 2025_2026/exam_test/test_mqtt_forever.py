import paho.mqtt.client as mqtt

client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id="test_client"
)
client.connect("test.mosquitto.org", 1883)
client.loop_forever()
