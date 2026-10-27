"""Rule-based controller of one room. It decides, it does not act: main applies the command."""


# thresholds for temperature and humidity


class Controller:
    def __init__(self, thresholds):
        self.t_max = thresholds["t_max"]
        self.t_min = thresholds["t_min"]
        self.h_max = thresholds["h_max"]
        # raise NotImplementedError("TODO Ex6: keep the thresholds dict (t_min, t_max, h_max)")

    def decide(self, measurements):
        """Return (command, alert). command is "ON", "OFF" or None (leave the HVAC as it is)."""
        command = None
        alert_string = "Everything is good!"
        if measurements["temperature"] <= self.t_min:
            command = "ON"
            alert_string = "Too cold! I'm switching on the HVAC"
        elif measurements["temperature"] >= self.t_max:
            command = "OFF"
            alert_string = "Too hot! I'm switching off the HVAC"
        else:
            pass

        if measurements["humidity"] > self.h_max:
            alert_string = "SOS - tooo water"

        return (command, alert_string)

        # raise NotImplementedError("TODO Ex6: temperature < t_min -> ON, > t_max -> OFF, else None; humidity > h_max -> alert string")
