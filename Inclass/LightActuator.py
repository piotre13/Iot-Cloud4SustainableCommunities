
from BaseActuator import BaseActuator as act

class LightActuator(act):
    def __init__(self, actuator_id, room):
        super().__init__(actuator_id, 'lightswitch', room)
    def actuate(self):
        print('HELLO SWITCHING LIGHT!')
        super().actuate()
        return self.state