# Ex1 - functions


def celsius_to_fahrenheit(c):
    f = c * 9 / 5 + 32
    return f


def is_too_cold(temp, t_min):
    if temp < t_min:
        print("It is too cold")
        return True
    else:
        return False


def is_too_hot(temp, t_max):
    if temp > t_max:
        print("It is too hot")
        return True
    else:
        return False


def hvac_command(temp, t_min, t_max):
    if is_too_hot(temp, t_max):
        return "OFF"
    elif is_too_cold(temp, t_min):
        return "ON"
    else:
        return None




if __name__ == "__main__":
    print(celsius_to_fahrenheit(20))  # 68.0
    print(is_too_cold(17.5, 19))  # True
    for temp in [17, 21, 26]:
        print(temp, "->", hvac_command(temp, 19, 23))
