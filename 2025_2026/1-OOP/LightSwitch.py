from BaseActuator import Actuator


class LightSwitch(Actuator):
    def __init__(self, actuator_id, room):
        super().__init__(actuator_id, "Light", room=room)

    def actuate(self):
        self.state = not self.state
        print(f"LightSwitch {self.actuator_id} is now {'ON' if self.state else 'OFF'}")
