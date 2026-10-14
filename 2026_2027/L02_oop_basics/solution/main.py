from devices import TemperatureSensor, HumiditySensor, HVAC

MENU = """
1) read sensors
2) HVAC ON
3) HVAC OFF
q) quit"""


def main():
    sensors = [TemperatureSensor(), HumiditySensor()]
    hvac = HVAC()

    while True:
        print(MENU)
        choice = input("> ").strip()
        if choice == "1":
            for sensor in sensors:  # polymorphism: same call, different sensors
                print(f"{sensor.name}: {sensor.sense()} {sensor.unit}")
        elif choice == "2":
            hvac.actuate("ON")
        elif choice == "3":
            hvac.actuate("OFF")
        elif choice == "q":
            break
        else:
            print(f"Invalid choice: {choice!r}")


if __name__ == "__main__":
    main()
