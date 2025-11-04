class Controller:
    def __init__(self, TH, rooms):
        self.threshold = TH
        self.rooms = rooms

    def check_rooms(self):
        correct = True
        for room, (sensor_id, actuator) in self.rooms.items():
            if sensor_id is None:
                print(f"Room '{room}' is missing a sensor.")
                correct = False
            if actuator is None:
                print(f"Room '{room}' is missing an actuator.")
                correct = False
        return correct

    def control(self, sensed_data):
        for room, (sensor_id, actuator) in self.rooms.items():
            if sensor_id in sensed_data:
                light_level = sensed_data[sensor_id]
                if light_level < self.threshold:
                    if not actuator.state:
                        actuator.actuate()
                else:
                    if actuator.state:
                        actuator.actuate()
