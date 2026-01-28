import cv2
import numpy as np

class CameraUtils:
    """
    Clase utilitaria para manejar la lógica de OpenCV:
    - Detección de rostros
    - Conversión de imágenes a bytes (y viceversa)
    - Reconocimiento facial (LBPH)
    """
    
    # Cargamos el clasificador pre-entrenado de Haar (viene con OpenCV)
    # Detecta patrones básicos de rostros (ojos, nariz, boca)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    @staticmethod
    def convertir_a_bytes(imagen_cv2):
        """
        Convierte una imagen de OpenCV (Matriz) a bytes para guardarla en la BD.
        Equivalente a guardar el archivo en disco pero en memoria RAM.
        """
        # Codificamos la imagen en formato JPG
        exito, buffer = cv2.imencode('.jpg', imagen_cv2)
        if exito:
            return buffer.tobytes() # Retorna los bytes crudos
        return None

    @staticmethod
    def bytes_a_imagen(blob_bytes):
        """
        Proceso inverso: Recibe bytes de la BD y los convierte a imagen OpenCV.
        Necesario para el entrenamiento del reconocedor.
        """
        # Convertimos la tira de bytes a un array de numpy
        nparr = np.frombuffer(blob_bytes, np.uint8)
        # Decodificamos la imagen
        return cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    @classmethod
    def detectar_rostro(cls, frame):
        """
        Recibe un fotograma de la cámara.
        Devuelve:
        - La cara recortada (si la encuentra)
        - Las coordenadas (x, y, w, h) para dibujar el recuadro
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detectamos rostros (scaleFactor=1.1, minNeighbors=5)
        rostros = cls.face_cascade.detectMultiScale(gray, 1.1, 5)
        
        if len(rostros) > 0:
            (x, y, w, h) = rostros[0] # Nos quedamos con la primera cara
            cara_recortada = gray[y:y+h, x:x+w]
            return cara_recortada, (x, y, w, h)
            
        return None, None

    @classmethod
    def entrenar_y_predecir(cls, lista_usuarios, cara_actual):
        """
        Implementa el 'Entrenamiento Lazy' (Perezoso):
        1. Descarga todas las fotos de la BD.
        2. Entrena el modelo en ese instante.
        3. Predice quién es la cara actual.
        """
        if not lista_usuarios:
            return "Sin usuarios", 0

        # Algoritmo de reconocimiento facial (LBPH)
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        rostros_entrenamiento = []
        ids_entrenamiento = []
        mapa_nombres = {} # Para traducir ID -> Nombre

        # Procesamos los datos que vienen del DAO
        # usuario = (id, nombre, cara_bytes)
        for usuario in lista_usuarios:
            user_id = usuario[0]
            nombre = usuario[1]
            cara_bytes = usuario[2]
            
            # Convertimos bytes a imagen útil para OpenCV
            imagen_rostro = cls.bytes_a_imagen(cara_bytes)
            
            if imagen_rostro is not None:
                rostros_entrenamiento.append(imagen_rostro)
                ids_entrenamiento.append(user_id)
                mapa_nombres[user_id] = nombre

        # Entrenamos el modelo con los datos actuales
        recognizer.train(rostros_entrenamiento, np.array(ids_entrenamiento))

        id_predicho, confianza = recognizer.predict(cara_actual)

        if confianza < 70:
            nombre_detectado = mapa_nombres.get(id_predicho, "Desconocido")
            return nombre_detectado, confianza
        else:
            return "Desconocido", confianza