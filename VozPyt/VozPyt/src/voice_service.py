import speech_recognition as sr

class VoiceService:
    """
    Patrón Facade: Proporciona una interfaz simple para interactuar con 
    el hardware del micrófono y la API de reconocimiento de voz.
    """
    
    @staticmethod
    def capturar_voz():
        """
        Activa el micrófono, escucha al usuario y traduce la voz a texto.
        Retorna una tupla: (texto_reconocido, confianza, estado/error)
        """
        recognizer = sr.Recognizer()
        
        # Usamos el micrófono del sistema
        with sr.Microphone() as source:
            print("Calibrando ruido de fondo (1 seg)... Por favor, en silencio.")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("¡Habla ahora! Di tu frase secreta...")
            try:
                # Escuchamos con un límite de tiempo para que no se quede colgado
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                print("Procesando el audio en la nube...")
                
                # Enviamos el audio a Google para que lo traduzca (requiere Internet)
                # show_all=True nos devuelve un JSON con más datos (como la confianza)
                resultado = recognizer.recognize_google(audio, language="es-ES", show_all=True)
                
                # Si Google no entendió nada o está vacío
                if not resultado or 'alternative' not in resultado:
                    return None, 0.0, "No se entendió el audio"
                
                # Extraemos la mejor opción que nos da la IA
                mejor_opcion = resultado['alternative'][0]
                texto = mejor_opcion['transcript'].lower()
                
                # Google a veces no devuelve la confianza exacta en la versión gratuita,
                # si no la da, ponemos un valor alto por defecto.
                confianza = mejor_opcion.get('confidence', 0.98)
                
                return texto, confianza, "OK"
                
            except sr.WaitTimeoutError:
                return None, 0.0, "Tiempo de espera agotado (No hablaste)"
            except sr.UnknownValueError:
                return None, 0.0, "No se pudo traducir el audio (Ruido incomprensible)"
            except sr.RequestError as e:
                return None, 0.0, f"Error de conexión con la IA: {e}"
            except Exception as e:
                return None, 0.0, f"Error hardware/software: {e}"