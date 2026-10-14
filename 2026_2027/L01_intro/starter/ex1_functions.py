# Ex1 - functions


def celsius_to_fahrenheit(c):
    raise NotImplementedError("TODO Ex1: return c * 9 / 5 + 32")


def is_too_cold(temp, t_min):
    raise NotImplementedError("TODO Ex1: return True if temp is below t_min")


def is_too_hot(temp, t_max):
    raise NotImplementedError("TODO Ex1: return True if temp is above t_max")


def hvac_command(temp, t_min, t_max):
    raise NotImplementedError("TODO Ex1: return 'ON' if too cold, 'OFF' if too hot, None otherwise (use the two helpers above)")


if __name__ == "__main__":
    print(celsius_to_fahrenheit(20))   # 68.0
    print(is_too_cold(17.5, 19))       # True
    for temp in [17, 21, 26]:
        print(temp, "->", hvac_command(temp, 19, 23))
