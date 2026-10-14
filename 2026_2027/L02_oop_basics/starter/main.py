from devices import TemperatureSensor, HumiditySensor, HVAC

MENU = """
1) read sensors
2) HVAC ON
3) HVAC OFF
q) quit"""


def main():
    sensors = [TemperatureSensor(), HumiditySensor()]
    hvac = HVAC()

    raise NotImplementedError("TODO Ex3: while True loop: print MENU, input(), then read sensors / HVAC ON / HVAC OFF / quit / invalid choice message")


if __name__ == "__main__":
    main()
