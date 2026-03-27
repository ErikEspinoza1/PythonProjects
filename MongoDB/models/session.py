from datetime import datetime

class Session:
    def __init__(self):
        # Al crear la sesión, guardamos la hora actual exacta
        self.start_time = datetime.now()
        self.end_time = None
        self.duration = None

    def end_session(self):
        # Al llamar a este método cuando cerremos el programa, calcula el tiempo total
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()

    def to_dict(self):
        # MongoDB necesita diccionarios (JSON), así que convertimos nuestro objeto
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration
        }