class Actuator:
    def __init__(self, actuator_id, actuator_type, room=None):
        self.actuator_id = actuator_id
        self.actuator_type = actuator_type
        self.room = room    
        self.state = False # Default state is off
        print(f"Actuator {self.actuator_id} of type {self.actuator_type} initialized.")

    def register(self):
        print(f"Registering Actuator, type: {self.actuator_type}, id: {self.actuator_id} in room {self.room}")

    def actuate(self):
        self.state = not self.state
        print(f"Actuating Actuator {self.actuator_id}: state is now {self.state}")
        return self.state