import os

class Config:
    # Si no defines una variable de entorno, creará el archivo 'coches.db' en tu carpeta
    DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///coches.db')