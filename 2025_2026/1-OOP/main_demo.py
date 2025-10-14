#!/usr/bin/env python3
"""
Simple IoT System Demo
Shows how Controller manages sensors and actuators in the same room
"""

import time

from Controller import Controller
from LightSensor import LightSensor
from LightSwitch import LightSwitch


def main():
    print("🏠 IoT Smart Home System Demo")
    print("=" * 40)

    # Create devices for living room
    print("\n🔧 Creating devices...")
    living_room_controller = Controller("Living Room")

    # Create sensors and actuators
    light_sensor = LightSensor("LS-001", "Living Room")
    light_switch = LightSwitch("SW-001", "Living Room")

    # Try to add a device from different room (should fail)
    wrong_room_sensor = LightSensor("LS-002", "Kitchen")

    print("\n📦 Adding devices to controller...")
    living_room_controller.add_sensor(light_sensor)
    living_room_controller.add_actuator(light_switch)
    living_room_controller.add_sensor(wrong_room_sensor)  # This should fail

    # Show initial status
    living_room_controller.status()

    print("\n🔄 Starting control loop...")

    # Run several control cycles
    for cycle in range(5):
        print(f"\n--- Cycle {cycle + 1} ---")
        living_room_controller.run_control_loop()
        time.sleep(1)  # Wait 1 second between cycles

    # Final status
    print("\n🏁 Final status:")
    living_room_controller.status()


if __name__ == "__main__":
    main()
