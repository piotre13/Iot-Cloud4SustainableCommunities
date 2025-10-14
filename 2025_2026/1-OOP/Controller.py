class Controller:
    """
    Simple IoT Controller that manages sensors and actuators in the same room.
    It reads sensor values and controls actuators based on simple rules.
    """

    def __init__(self, room_name):
        self.room_name = room_name
        self.sensors = []
        self.actuators = []
        print(f"Controller initialized for room: {self.room_name}")

    def add_sensor(self, sensor):
        """Add a sensor to this controller (must be in the same room)"""
        if sensor.room == self.room_name:
            self.sensors.append(sensor)
            print(f"✅ Added sensor {sensor.sensor_id} to {self.room_name} controller")
        else:
            print(
                f"❌ Cannot add sensor {sensor.sensor_id} - room mismatch ({sensor.room} != {self.room_name})"
            )

    def add_actuator(self, actuator):
        """Add an actuator to this controller (must be in the same room)"""
        if actuator.room == self.room_name:
            self.actuators.append(actuator)
            print(
                f"✅ Added actuator {actuator.actuator_id} to {self.room_name} controller"
            )
        else:
            print(
                f"❌ Cannot add actuator {actuator.actuator_id} - room mismatch ({actuator.room} != {self.room_name})"
            )

    def read_sensors(self):
        """Read values from all sensors in this room"""
        sensor_data = {}
        print(f"\n📊 Reading sensors in {self.room_name}:")
        for sensor in self.sensors:
            value = sensor.sense()
            sensor_data[sensor.sensor_type] = value
        return sensor_data

    def control_actuators(self, sensor_data):
        """Simple control logic based on sensor readings"""
        print(f"\n🎛️  Controlling actuators in {self.room_name}:")

        # Simple rule: if light is low, turn on lights
        if "Light" in sensor_data:
            light_level = sensor_data["Light"]
            for actuator in self.actuators:
                if actuator.actuator_type == "Light":
                    if light_level < 50 and not actuator.state:
                        print(
                            f"💡 Light level ({light_level}) is low, turning ON light"
                        )
                        actuator.actuate()
                    elif light_level >= 200 and actuator.state:
                        print(
                            f"☀️ Light level ({light_level}) is high, turning OFF light"
                        )
                        actuator.actuate()

    def run_control_loop(self):
        """Main control loop: read sensors and control actuators"""
        print(f"\n🔄 Running control loop for {self.room_name}")
        print("=" * 50)

        # Read all sensors
        sensor_data = self.read_sensors()

        # Control actuators based on sensor data
        self.control_actuators(sensor_data)

        print("=" * 50)
        return sensor_data

    def status(self):
        """Display current status of all devices in this room"""
        print(f"\n📋 Status for room: {self.room_name}")
        print(f"Sensors: {len(self.sensors)}, Actuators: {len(self.actuators)}")

        for sensor in self.sensors:
            print(f"  📡 {sensor.sensor_type} sensor: {sensor.sensor_id}")

        for actuator in self.actuators:
            state_icon = "🟢" if actuator.state else "🔴"
            print(
                f"  {state_icon} {actuator.actuator_type} actuator: {actuator.actuator_id} ({'ON' if actuator.state else 'OFF'})"
            )
