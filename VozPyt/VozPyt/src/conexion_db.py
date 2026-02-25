import psycopg2
from src.config import Config

class DBConnection:
    _connection = None

    @classmethod
    def get_connection(cls):
        if cls._connection is None or cls._connection.closed != 0:
            try:
                params = Config.get_db_params()
                cls._connection = psycopg2.connect(**params)
                print("Conexión a Base de Datos establecida.")
            except Exception as e:
                print(f"Error al conectar a la BD: {e}")
                return None
        return cls._connection