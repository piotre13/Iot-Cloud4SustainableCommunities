class BaseActuator:
    def __init__(self, id, typology, room, state=False):
        self.id = id
        self.typology = typology
        self.room = room
        self.state = state

    def register(self):
        print(
            f"Registering actuator {self.id} of type {self.typology} in room: {self.room}"
        )

    def actuate(self):
        print("Actuate!!!")
        self.state = not self.state
        return self.state


if __name__ == "__main__":
    # Simple test
    actuator = BaseActuator("A-001", "Light", "Living Room")
    actuator.register()
    print(f"Initial state: {actuator.state}")
    state=actuator.actuate()
    print(f"New state: {actuator.state}")
