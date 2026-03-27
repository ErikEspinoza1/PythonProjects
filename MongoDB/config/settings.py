import os
from dotenv import load_dotenv

# Carga las variables que pusimos en el archivo .env
load_dotenv()

# Guardamos las variables en constantes para usarlas en el proyecto
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Un pequeño aviso por si algo falla al leer el .env
if not MONGODB_URI:
    print("⚠️ ADVERTENCIA: No se ha encontrado MONGODB_URI en el archivo .env")