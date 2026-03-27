from datetime import datetime

class VolumeEvent:
    def __init__(self, old_volume, new_volume, finger_distance):
        self.timestamp = datetime.now()
        self.old_volume = old_volume
        self.new_volume = new_volume
        self.finger_distance = finger_distance

    def to_dict(self):
        # Convertimos los datos a formato diccionario para MongoDB
        return {
            "timestamp": self.timestamp,
            "old_volume": self.old_volume,
            "new_volume": self.new_volume,
            "finger_distance": self.finger_distance
        }