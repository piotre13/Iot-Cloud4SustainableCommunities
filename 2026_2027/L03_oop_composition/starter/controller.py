"""Rule-based controller of one room. It decides, it does not act: main applies the command."""


class Controller:
    def __init__(self, thresholds):
        raise NotImplementedError("TODO Ex6: keep the thresholds dict (t_min, t_max, h_max)")

    def decide(self, measurements):
        """Return (command, alert). command is "ON", "OFF" or None (leave the HVAC as it is)."""
        raise NotImplementedError("TODO Ex6: temperature < t_min -> ON, > t_max -> OFF, else None; humidity > h_max -> alert string")
