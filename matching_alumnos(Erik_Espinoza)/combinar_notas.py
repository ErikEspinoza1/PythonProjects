import csv
import os
FOLDER_PATH = "."
FILE_UF1 = os.path.join(FOLDER_PATH, 'notas_alumnos_UF1.csv')
FILE_UF2 = os.path.join(FOLDER_PATH, 'notas_alumnos_UF2.csv')
FILE_OUTPUT = os.path.join(FOLDER_PATH, 'notas_alumnos.csv')

DELIMITER = ';'

datos_combinados = {}
nombres_columnas_salida = ["Id", "Apellidos", "Nombre", "UF1", "UF2"]

try:
    with open(FILE_UF1, 'r', newline='', encoding='utf-8') as file_uf1:
        reader_uf1 = csv.DictReader(file_uf1, delimiter=DELIMITER)

        for fila in reader_uf1:
            id_alumno = fila['Id'].strip()

            datos_combinados[id_alumno] = {
                "Id": id_alumno,
                "Apellidos": fila['Apellidos'].strip(),
                "Nombre": fila['Nombre'].strip(),
                "UF1": fila['UF1'].strip(),
                "UF2": ""
            }

    with open(FILE_UF2, 'r', newline='', encoding='utf-8') as file_uf2:
        reader_uf2 = csv.DictReader(file_uf2, delimiter=DELIMITER)
        for fila in reader_uf2:
            id_alumno = fila['Id'].strip()

            if id_alumno in datos_combinados:
                datos_combinados[id_alumno]["UF2"] = fila['UF2'].strip()
            else:
                print(f"Advertencia: El alumno con Id {id_alumno} está en UF2 pero no en UF1. Se añadirá.")
                datos_combinados[id_alumno] = {
                    "Id": id_alumno,
                    "Apellidos": fila['Apellidos'].strip(),
                    "Nombre": fila['Nombre'].strip(),
                    "UF1": "",
                    "UF2": fila['UF2'].strip()
                }

    with open(FILE_OUTPUT, 'w', newline='', encoding='utf-8') as file_output:
        writer = csv.DictWriter(
            file_output,
            fieldnames=nombres_columnas_salida,
            delimiter=DELIMITER
        )

        writer.writeheader()

        for id_alumno in sorted(datos_combinados.keys()):
            writer.writerow(datos_combinados[id_alumno])

    print(f"\n Éxito: Los datos se han combinado y guardado en '{FILE_OUTPUT}'")

except FileNotFoundError:
    print(
        f"\n Error: Asegúrate de que los archivos de entrada ({os.path.basename(FILE_UF1)} y {os.path.basename(FILE_UF2)}) existen en la ruta: {FOLDER_PATH}")
except Exception as e:
    print(f"\n Ha ocurrido un error inesperado: {e}")