import psycopg2
from src.conexion_db import DBConnection

class UsuarioDAO:
    """
    Data Access Object para la tabla 'usuarios'.
    Se encarga de todas las operaciones CRUD (Create, Read, Update, Delete).
    """

    @classmethod
    def registrar_usuario(cls, nombre, foto_bytes, cara_bytes):
        """
        Guarda un nuevo usuario con sus imágenes en binario (BLOBs).
        """
        # 1. Obtenemos la conexión del Singleton
        conn = DBConnection.get_connection()
        if conn is None:
            print(" Error: No hay conexión a la base de datos.")
            return False

        try:
            # 2. Preparamos el cursor para ejecutar SQL
            cursor = conn.cursor()
            
            # 3. La consulta SQL Segura (Evita inyección SQL)
            sql = """
                INSERT INTO usuarios (nombre, foto_bytes, cara_bytes)
                VALUES (%s, %s, %s);
            """
            
            # 4. Convertimos los bytes crudos a formato binario de PostgreSQL
            params = (
                nombre, 
                psycopg2.Binary(foto_bytes), 
                psycopg2.Binary(cara_bytes)
            )
            
            # 5. Ejecutamos y confirmamos (Commit)
            cursor.execute(sql, params)
            conn.commit()
            
            print(f"✅ Usuario '{nombre}' registrado con éxito.")
            cursor.close()
            return True

        except Exception as e:
            print(f"❌ Error al registrar usuario: {e}")
            conn.rollback()
            return False

    @classmethod
    def obtener_todos(cls):
        """
        Recupera todos los usuarios para entrenar el reconocimiento facial.
        """
        conn = DBConnection.get_connection()
        if conn is None: return []

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, cara_bytes FROM usuarios;")
            usuarios = cursor.fetchall()
            cursor.close()
            return usuarios
        except Exception as e:
            print(f"❌ Error al obtener usuarios: {e}")
            return []