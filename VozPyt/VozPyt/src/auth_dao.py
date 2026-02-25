import json
from src.conexion_db import DBConnection

class AuthDAO:
    """
    Data Access Object para manejar la autenticación y los logs dinámicos.
    Separa la lógica de base de datos de la interfaz de usuario.
    """

    @classmethod
    def registrar_usuario(cls, username, passphrase, log_data):
        """
        Registra un usuario y crea su primer log de acceso en la misma transacción.
        """
        conn = DBConnection.get_connection()
        if not conn: return False

        try:
            cursor = conn.cursor()
            
            # 1. Insertar el usuario y recuperar su ID autogenerado
            sql_user = """
                INSERT INTO usuarios_voz (username, passphrase)
                VALUES (%s, %s) RETURNING id;
            """
            cursor.execute(sql_user, (username, passphrase))
            usuario_id = cursor.fetchone()[0]

            # 2. Insertar el log inicial usando la columna JSONB
            sql_log = """
                INSERT INTO log_accesos_voz (usuario_id, resultado_json)
                VALUES (%s, %s);
            """
            # json.dumps convierte el diccionario de Python en texto compatible con JSONB
            cursor.execute(sql_log, (usuario_id, json.dumps(log_data)))

            # Confirmamos ambas operaciones
            conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            print(f"Error al registrar usuario/log: {e}")
            conn.rollback() # Si falla, deshacemos todo para evitar datos a medias
            return False

    @classmethod
    def obtener_usuario(cls, username):
        """Busca un usuario por su nombre para el proceso de Login"""
        conn = DBConnection.get_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            sql = "SELECT id, passphrase, intentos_fallidos, bloqueado_hasta FROM usuarios_voz WHERE username = %s;"
            cursor.execute(sql, (username,))
            user = cursor.fetchone() # Retorna (id, passphrase, intentos, bloqueado)
            cursor.close()
            return user
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None

    @classmethod
    def registrar_log(cls, usuario_id, log_data):
        """Añade un nuevo evento a la bolsa dinámica de logs (JSONB)"""
        conn = DBConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            sql = "INSERT INTO log_accesos_voz (usuario_id, resultado_json) VALUES (%s, %s);"
            cursor.execute(sql, (usuario_id, json.dumps(log_data)))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error al guardar log: {e}")
            conn.rollback()
            return False

    @classmethod
    def actualizar_intentos(cls, usuario_id, intentos, bloqueado_hasta=None):
        """Actualiza el contador de fallos y el posible bloqueo del usuario"""
        conn = DBConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            sql = "UPDATE usuarios_voz SET intentos_fallidos = %s, bloqueado_hasta = %s WHERE id = %s;"
            cursor.execute(sql, (intentos, bloqueado_hasta, usuario_id))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error al actualizar intentos: {e}")
            conn.rollback()
            return False

    @classmethod
    def obtener_auditoria_critica(cls):
        """
        Ejecuta una consulta avanzada que extrae datos directamente desde 
        el interior del campo JSONB.
        """
        conn = DBConnection.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            # Esta es la consulta requerida en las instrucciones de la práctica
            sql = """
                SELECT u.username, l.resultado_json->>'status', l.resultado_json
                FROM log_accesos_voz l
                JOIN usuarios_voz u ON l.usuario_id = u.id
                WHERE l.resultado_json->>'status' = 'FAIL'
                   OR (l.resultado_json->>'confianza')::float < 0.6;
            """
            cursor.execute(sql)
            registros = cursor.fetchall()
            cursor.close()
            return registros
        except Exception as e:
            print(f"Error en auditoría: {e}")
            return []