from pymongo import MongoClient
from config.settings import MONGODB_URI, DATABASE_NAME

class MongoDBDAO:
    _instance = None  # Variable secreta para el Singleton

    def __new__(cls):
        # Magia del Patrón Singleton: si no hay conexión, la crea. Si ya hay, la reutiliza.
        if cls._instance is None:
            cls._instance = super(MongoDBDAO, cls).__new__(cls)
            cls._instance._connect()
        return cls._instance

    def _connect(self):
        """Establece la conexión con MongoDB Atlas."""
        try:
            self.client = MongoClient(MONGODB_URI)
            self.db = self.client[DATABASE_NAME]
            
            # Preparamos las colecciones donde guardaremos las sesiones y los cambios de volumen
            self.sessions_collection = self.db["sessions"]
            self.events_collection = self.db["volume_events"]
            print("✅ DAO: Conectado a MongoDB Atlas correctamente.")
        except Exception as e:
            print(f"❌ Error conectando a la base de datos: {e}")
            self.db = None
            
    def test_connection(self):
        """Devuelve True si la conexión está viva (para el indicador visual en pantalla)."""
        return self.db is not None

    # --- NUEVOS MÉTODOS PARA GUARDAR DATOS ---

    def save_session(self, session):
        """Guarda los datos de la sesión en MongoDB Atlas."""
        if self.db is not None:
            try:
                # Usamos el método to_dict() que creamos en el modelo Session
                self.sessions_collection.insert_one(session.to_dict())
                print("✅ Sesión guardada en la base de datos.")
            except Exception as e:
                print(f"❌ Error al guardar la sesión: {e}")

    def save_volume_event(self, event):
        """Guarda un evento de cambio de volumen en MongoDB Atlas."""
        if self.db is not None:
            try:
                # Usamos el método to_dict() que creamos en el modelo VolumeEvent
                self.events_collection.insert_one(event.to_dict())
                print("🔊 Evento de volumen registrado en la BD.")
            except Exception as e:
                print(f"❌ Error al guardar el evento: {e}")