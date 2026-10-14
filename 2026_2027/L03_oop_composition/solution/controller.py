"""Rule-based controller of one room. It decides, it does not act: main applies the command."""


class Controller:
    def __init__(self, thresholds):
        self.thresholds = thresholds

    def decide(self, measurements):
        """Return (command, alert). command is "ON", "OFF" or None (leave the HVAC as it is)."""
        t = self.thresholds
        command = None
        if measurements["temperature"] < t["t_min"]:
            command = "ON"
        elif measurements["temperature"] > t["t_max"]:
            command = "OFF"

        alert = None
        if measurements["humidity"] > t["h_max"]:
            alert = f"humidity {measurements['humidity']:g}% > {t['h_max']}%"
        return command, alert
