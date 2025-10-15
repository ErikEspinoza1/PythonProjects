class Alumno:
    def __init__(self, nombre: str):
        self._nombre = nombre

    @property
    def nombre(self):
        return self._nombre
    def __str__(self):
        return f'Alumno: {self.nombre}'
