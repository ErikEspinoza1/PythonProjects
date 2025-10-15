from dominio.alumno import Alumno
import os


class AlumnosMatriculados:
    ruta_archivo = 'alumnos.txt'

    @staticmethod
    def matricular_alumno(alumno: Alumno):
        """Añade un alumno al final del archivo."""
        try:
            with open(AlumnosMatriculados.ruta_archivo, 'a') as archivo:
                archivo.write(f'{alumno.nombre}\n')
            print(f"✅ Alumno '{alumno.nombre}' matriculado correctamente.")
        except Exception as e:
            print(f"❌ Error al matricular alumno: {e}")

    @staticmethod
    def listar_alumnos():
        """Lee y muestra todos los alumnos del archivo."""
        try:
            if os.path.exists(AlumnosMatriculados.ruta_archivo):
                with open(AlumnosMatriculados.ruta_archivo, 'r') as archivo:
                    print("\n--- Lista de Alumnos Matriculados ---")
                    contenido = archivo.read()
                    if contenido:
                        print(contenido.strip()) 
                    else:
                        print("(No hay alumnos matriculados)")
                    print("------------------------------------")
            else:
                print("ℹ️  Aún no se ha creado el archivo de alumnos.")
        except Exception as e:
            print(f"❌ Error al listar alumnos: {e}")

    @staticmethod
    def eliminar_alumnos():
        """Elimina el archivo de alumnos."""
        try:
            if os.path.exists(AlumnosMatriculados.ruta_archivo):
                os.remove(AlumnosMatriculados.ruta_archivo)
                print("✅ Archivo de alumnos eliminado correctamente.")
            else:
                print("ℹ️  El archivo de alumnos no existe, no hay nada que eliminar.")
        except Exception as e:
            print(f"❌ Error al eliminar el archivo: {e}")