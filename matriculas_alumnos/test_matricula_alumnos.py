from dominio.alumno import Alumno
from servicio.alumnos_matriculados import AlumnosMatriculados

def mostrar_menu():
    """Función que muestra el menú de opciones."""
    print("\n--- Menú de Matrícula de Alumnos ---")
    print("1. Matricular un alumno")
    print("2. Listar alumnos matriculados")
    print("3. Eliminar archivo de alumnos")
    print("4. Salir")
    print("------------------------------------")

def main():
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción: ")

        if opcion == '1':
            nombre = input("Introduce el nombre del alumno a matricular: ")
            nuevo_alumno = Alumno(nombre)
            AlumnosMatriculados.matricular_alumno(nuevo_alumno)

        elif opcion == '2':
            AlumnosMatriculados.listar_alumnos()

        elif opcion == '3':
            AlumnosMatriculados.eliminar_alumnos()

        elif opcion == '4':
            print(" Saliendo del programa. ¡Hasta pronto!")
            break
        
        else:
            print(" Opción no válida. Por favor, elige un número del 1 al 4.")

if __name__ == "__main__":
    main()
