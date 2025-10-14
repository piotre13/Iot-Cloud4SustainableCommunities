from LightSensor import LightSensor
from LightSwitch import LightSwitch
import time

if __name__ == "__main__":
    sensors = {}
    actuators = {}

    # loop for population of sensors and actuators using input from command line
    while True:
        command = input("Enter command (add_sensor, add_actuator, simulate): ").strip()

        if command == "add_sensor":
            sensor_id = input("Enter sensor ID: ").strip()
            room = input("Enter room (optional): ").strip() or None
            sensors[sensor_id] = LightSensor(sensor_id, room)
            print(f"Added LightSensor with ID {sensor_id} in room {room}")

        elif command == "add_actuator":
            actuator_id = input("Enter actuator ID: ").strip()
            room = input("Enter room: ").strip()
            actuators[actuator_id] = LightSwitch(actuator_id, room)
            print(f"Added LightSwitch with ID {actuator_id} in room {room}")

        elif command == "simulate":
            time_steps = int(input("Enter number of time steps to simulate: ").strip())
            break
        else:
            print("Unknown command. Please try again.")


for i in range(time_steps):
    print(f"\n--- Time Step {i + 1} ---")
    time.sleep(5)  # Simulate time passing
    for sensor in sensors.values():
        sensor.sense()
    for actuator in actuators.values():
        actuator.actuate()  # Toggle state each time step
