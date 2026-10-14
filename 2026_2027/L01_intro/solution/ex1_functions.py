# Ex1 - functions


def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32


def is_too_cold(temp, t_min):
    return temp < t_min


def is_too_hot(temp, t_max):
    return temp > t_max


def hvac_command(temp, t_min, t_max):
    """Return 'ON' if too cold, 'OFF' if too hot, None inside the band (leave the HVAC as it is)."""
    if is_too_cold(temp, t_min):
        return "ON"
    if is_too_hot(temp, t_max):
        return "OFF"
    return None


if __name__ == "__main__":
    print(celsius_to_fahrenheit(20))   # 68.0
    print(is_too_cold(17.5, 19))       # True
    for temp in [17, 21, 26]:
        print(temp, "->", hvac_command(temp, 19, 23))
