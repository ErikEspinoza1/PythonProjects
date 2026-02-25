from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.config.config import Config

# 1. Crear el motor de conexión
engine = create_engine(Config.DATABASE_URI)

# 2. Crear la fábrica de sesiones
Session = sessionmaker(bind=engine)
session = Session()

# 3. Crear la clase base para tus modelos
Base = declarative_base()