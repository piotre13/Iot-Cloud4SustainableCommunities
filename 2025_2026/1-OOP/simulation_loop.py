import time

from Controller import Controller
from LightSensor import LightSensor as sensor
from LightSwitch import LightSwitch as actuator

sensor_list = []
actuator_list = []
sensed_data = {}
rooms = {}

while True:
    command = input(
        "Enter a command:\n new_sens,\n new_act \n start_sim\n quit :\n"
    )  # ask user to type a command

    if command in [
        "new_sens",
        "new_act",
        "start_sim",
        "quit",
    ]:  # Validate command input
        if command == "start_sim":
            if not rooms:
                print(
                    "No rooms registered. Please add sensor and actuator for rooms first."
                )
                continue
            try:
                simul_ts = int(input("how many steps:\n"))
                freq = int(input("at which frequency (seconds):\n"))
            except ValueError:
                print(
                    "Invalid input. Please enter integer values for steps and frequency."
                )
                continue

            controller = Controller(TH=700, rooms=rooms)  # Set a default threshold
            if not controller.check_rooms():
                continue
            for _ in range(simul_ts):
                # to be continued
                for s in sensor_list:
                    val = s.sense()
                    sensed_data[s.sensor_id] = val
                controller.control(sensed_data)
                time.sleep(freq)

        elif command == "new_sens":
            room = input("Enter room name for the sensor:\n")
            if room in rooms.keys() and rooms[room][0] is not None:
                print("Room already with sensor. NO more.")
            elif room in rooms.keys() and rooms[room][0] is None:
                sensor_id = f"{room}-LS-{len(sensor_list) + 1}"
                new_sensor = sensor(sensor_id, room)
                sensor_list.append(new_sensor)
                rooms[room][0] = sensor_id

            else:
                sensor_id = f"{room}-LS-{len(sensor_list) + 1}"
                new_sensor = sensor(sensor_id, room)
                sensor_list.append(new_sensor)
                rooms[room] = [sensor_id, None]

        elif command == "new_act":
            room = input("Enter room name for the actuator:\n")
            if room in rooms.keys() and rooms[room][1] is not None:
                print("Room already with actuator. NO more.")

            elif room in rooms.keys() and rooms[room][1] is None:
                actuator_id = f"{room}-LS-{len(actuator_list) + 1}"
                new_actuator = actuator(actuator_id, room)
                actuator_list.append(new_actuator)
                rooms[room][1] = new_actuator
            else:
                actuator_id = f"{room}-LS-{len(actuator_list) + 1}"
                new_actuator = actuator(actuator_id, room)
                actuator_list.append(new_actuator)
                rooms[room] = [None, new_actuator]

        elif command == "quit":
            break
    else:
        print("Invalid command. Please try again.")
