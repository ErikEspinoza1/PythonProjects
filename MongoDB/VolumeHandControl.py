import cv2
import numpy as np
# Ya no necesitamos ctypes ni comtypes, la nueva versión lo hace solo
from pycaw.pycaw import AudioUtilities

class VolumeController:
    def __init__(self):
        # La nueva forma de conectar con el audio de Windows (¡mucho más fácil!)
        device = AudioUtilities.GetSpeakers()
        self.volume = device.EndpointVolume
        
        # Rango de volumen: suele ser -65.25 (mín) a 0.0 (máx)
        volRange = self.volume.GetVolumeRange()
        self.minVol = volRange[0]
        self.maxVol = volRange[1]
        self.volBar = 400
        self.volPer = 0

    def update_volume(self, length):
        """Mapea la distancia de dedos al volumen del sistema."""
        # Convertimos la distancia (50-250px) al rango de audio (-65 a 0)
        vol = np.interp(length, [50, 250], [self.minVol, self.maxVol])
        self.volBar = np.interp(length, [50, 250], [400, 150])
        self.volPer = np.interp(length, [50, 250], [0, 100])
        
        self.volume.SetMasterVolumeLevel(vol, None)
        return self.volPer

    def draw_ui(self, img):
        """Dibuja la barra de volumen visual requerida."""
        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
        cv2.rectangle(img, (50, int(self.volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
        cv2.putText(img, f'{int(self.volPer)} %', (40, 450), 
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
        return img