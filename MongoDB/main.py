import cv2
import time
from HandTrackingModule import HandDetector
from VolumeHandControl import VolumeController
from dao.mongodb_dao import MongoDBDAO
from models.session import Session
from models.volume_event import VolumeEvent

def main():
    # 1. Inicialización de componentes
    cap = cv2.VideoCapture(0)
    detector = HandDetector(detectionCon=0.8)
    vol_control = VolumeController()
    dao = MongoDBDAO()
    
    # Iniciar sesión en el modelo
    current_session = Session()
    last_vol = 0
    
    # Guardamos el nombre de la ventana para poder controlarla luego
    window_name = "Control de Volumen por Gestos"
    
    print("🚀 Aplicación iniciada. Pulsa 'q' o cierra la ventana para salir.")

    while True:
        success, img = cap.read()
        if not success: break
        
        # 2. Detección de manos
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img, draw=True)
        
        # Indicador de conexión a DB
        status_db = "DB: OK" if dao.test_connection() else "DB: --"
        cv2.putText(img, status_db, (450, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        if len(lmList) != 0:
            # Detectar si el meñique está bajado (puntos 20 y 18)
            if lmList[20][2] > lmList[18][2]: 
                # Medir distancia pulgar (4) e índice (8)
                length, img, _ = detector.findDistance(4, 8, img)
                
                # Actualizar volumen y registrar evento
                new_vol = vol_control.update_volume(length)
                
                if abs(new_vol - last_vol) > 2: # Solo guardar si hay cambio real
                    event = VolumeEvent(last_vol, new_vol, length)
                    dao.save_volume_event(event)
                    last_vol = new_vol

            vol_control.draw_ui(img)

        # 3. Mostrar la ventana
        cv2.imshow(window_name, img)
        
        # --- NUEVA LÓGICA DE CIERRE ---
        # Opción A: Salir con la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break
            
        # Opción B: Salir si el usuario pulsa la 'X' de la ventana de Windows
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

    # 4. Finalizar y guardar sesión en MongoDB
    print("Cerrando la aplicación y guardando datos...")
    current_session.end_session()
    dao.save_session(current_session)
    cap.release()
    cv2.destroyAllWindows()
    print("¡Sesión terminada con éxito!")

if __name__ == "__main__":
    main()