from devices import HVAC, HumiditySensor, TemperatureSensor

MENU = """
1) read sensors
2) HVAC ON
3) HVAC OFF
q) quit"""


def main():
    sensors = [TemperatureSensor(), HumiditySensor(), TemperatureSensor()]
    hvac = HVAC()
    while True:
        print(MENU + "\n")
        command = input("insert command: ")
        if command == "read sensors":
            for sens in sensors:
                print(sens.sense())

        elif command == "HVAC ON":
            hvac.actuate("ON")
            print(hvac.state)

        elif command == "HVAC OFF":
            hvac.actuate("OFF")
            print(hvac.state)

        elif command == "quit":
            break


if __name__ == "__main__":
    main()
