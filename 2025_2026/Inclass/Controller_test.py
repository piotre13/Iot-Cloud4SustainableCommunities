class Controller:
    def __init__(self):
        self.rooms = {}
        self.TH = 45  # Threshold value for light sensor
    
    def register_rooms(self, sensor_list, actuator_list):
        for sensor in sensor_list:
            if sensor.room in self.rooms.keys():
                self.rooms[sensor.room]["sensor"] = sensor
            for actuator in actuator_list:
                if sensor.room == actuator.room:
                    self.rooms[sensor.room] = {"sensor": sensor, "actuator": actuator}
                    break

    def control_step(self, sensed_data):
        for room in self.rooms.values():
            sens_name = room["sensor"].id
            val = sensed_data.get(sens_name, None)

            if val is not None:
                if val < self.TH:
                    if not room["actuator"].state:
                        room["actuator"].actuate()
                else:
                    if room["actuator"].state:
                        room["actuator"].actuate()



class Controller_base:
    def __init__(self):
        self.rooms = {}
        self.threshold = 30

    def check_thresholds(self, sensed_data):
        control_actions = {}
        for room in self.rooms.values():
            sens_name = room["sensor"]
            act_name = room["actuator"]
            val = sensed_data.get(sens_name, None)
            if val is not None:
                if val < self.threshold:
                    control_actions[act_name] = True
                else:
                    control_actions[act_name] = False
        return control_actions
        


if __name__ == "__main__":
    from Inclass.LightActuator_ex import LightActuator
    from Inclass.LightSensor_class import LightSensor

    sensor1 = LightSensor("LS-001", "LivingRoom")
    actuator1 = LightActuator("LA-001", "LivingRoom")
    controller = Controller()

    controller.rooms = {"LivingRoom": {"sensor": sensor1, "actuator": actuator1}}

    sensed_data = {"LS-001": None}

    for _ in range(10):
        sensed_data["LS-001"] = sensor1.sense()
        controller.control_step(sensed_data)
