from sqlalchemy import Column, Integer, String, Float
from src.config.db import Base

class Coche(Base):
    __tablename__ = 'coches'

    # Definición de columnas (atributos del coche)
    id = Column(Integer, primary_key=True)
    marca = Column(String)
    modelo = Column(String)
    anyo = Column(Integer)
    precio = Column(Float)