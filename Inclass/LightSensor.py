import os
import random
import sys
from datetime import datetime

from BaseSensor import Sensor


class LightSensor(Sensor):
    def __init__(self, sensor_id, room=None):
        super().__init__(sensor_id, "Light", room)

    def sense(self):
        current_hour = datetime.now().hour

        # Base light level based on time of day
        if 6 <= current_hour < 8:  # Dawn
            base_light = 20 + (current_hour - 6) * 30  # 20-80 lux
        elif 8 <= current_hour < 18:  # Day
            base_light = 800 + random.gauss(0, 200)  # 600-1000+ lux (cloudy to sunny)
        elif 18 <= current_hour < 20:  # Dusk
            base_light = 80 - (current_hour - 18) * 35  # 80-10 lux
        else:  # Night (20-6)
            base_light = 2 + random.exponential(3)  # 0-15 lux (mostly low)

        # Add some realistic noise and weather variations
        weather_factor = random.uniform(0.7, 1.3)  # Simulate cloud coverage
        noise = random.uniform(-5, 5)

        final_value = max(0, min(1000, base_light * weather_factor + noise))

        print(
            f"Light Sensor {self.sensor_id} in room {self.room} sensing value: {final_value:.1f} lux (Hour: {current_hour}:00)"
        )
        return round(final_value, 1)
