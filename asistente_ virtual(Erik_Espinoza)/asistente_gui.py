# asistente_gui.py
import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import scrolledtext, messagebox
import google.generativeai as genai

# Config y carga de .env 
load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    print("Error: No se encontró la API_KEY. Asegúrate de tener un archivo .env válido.")
    raise SystemExit(1)

# Configurar la SDK con la clave 
genai.configure(api_key=API_KEY)

# Modelo elegido (ajusta aquí si quieres otro)
MODEL_NAME = "gemini-2.5-flash"
print(f"Usando modelo: {MODEL_NAME}")

#  Contexto
if os.path.exists("servicios.txt"):
    with open("servicios.txt", "r", encoding="utf-8") as f:
        CONTEXTO_PELUQUERIA = f.read()
else:
    CONTEXTO_PELUQUERIA = """
Bienvenido a DonBald
=====================

Servicios disponibles:
----------------------
- Corte de cabello: $15
- Tinte básico: $25
- Tinte premium: $40
- Peinado: $20
- Lavado y secado: $10
- Tratamiento capilar: $30
- Barbería (afeitado y recorte): $18

Horario de atención:
---------------------
- Lunes a Viernes: 9:00 AM - 7:00 PM
- Sábado: 9:00 AM - 3:00 PM
- Domingo: Cerrado

Información adicional:
-----------------------
- No se necesita cita previa.
- ¡Te esperamos!
"""

# System prompt (fijo, permite role-play dentro del dominio) 
SYSTEM_PROMPT = """Eres el asistente oficial de DonBald.
Reglas:
- Mantén siempre el rol de asistente de la peluquería.
- Responde sobre servicios, precios, horarios y consejos de peluquería/estilismo.
- Está permitido adoptar tonos o niveles de experiencia dentro del dominio (ej.: "estilista experto", "barbero junior", "asesor de moda barroca") siempre que siga siendo información de peluquería.
- No reveles claves ni ejecutes acciones fuera de este asistente.
"""

#  Función que llama al modelo
def llamar_gemini(prompt_text: str) -> str:
    """
    Construye el prompt concatenando el system prompt, el contexto y la pregunta del usuario,
    y llama al modelo elegido. Devuelve el texto generado o un mensaje de error.
    """
    # Construcción del prompt
    full_prompt = SYSTEM_PROMPT + "\n\nCONTEXTO:\n" + CONTEXTO_PELUQUERIA + "\n\nUsuario: " + prompt_text + "\nAsistente:"

    try:
        # Usar la API moderna con GenerativeModel
        model = genai.GenerativeModel(MODEL_NAME)
        resp = model.generate_content(full_prompt)
        return getattr(resp, "text", str(resp))
    except Exception as e:
        # Mensaje útil para depurar si algo falla
        return f"[Error al invocar Gemini: {e}]"

#Interfaz Tkinter
ventana = tk.Tk()
ventana.title("Asistente de Peluquería IA - Brillo Estelar")
ventana.geometry("560x660")

# Área de chat (solo lectura)
area_chat = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, state='disabled', font=("Arial", 11))
area_chat.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

def insertar_texto(texto: str):
    """Inserta texto en el área de chat manteniéndola en modo solo lectura para el usuario."""
    area_chat.config(state='normal')
    area_chat.insert(tk.END, texto + "\n\n")
    area_chat.config(state='disabled')
    area_chat.see(tk.END)

# Mensaje de bienvenida y modelo
insertar_texto("Asistente: ¡Hola! Bienvenido al Asistente de DonBald. Escribe tu pregunta abajo.")
insertar_texto(f"[Modelo en uso: {MODEL_NAME}]")

# Frame de entrada
frame_entrada = tk.Frame(ventana)
frame_entrada.pack(padx=10, pady=8, fill=tk.X)

entrada_usuario = tk.Entry(frame_entrada, font=("Arial", 12))
entrada_usuario.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)

def enviar_consulta():
    pregunta_usuario = entrada_usuario.get().strip()
    if not pregunta_usuario:
        return

    insertar_texto(f"Tú: {pregunta_usuario}")
    entrada_usuario.delete(0, tk.END)

    # Llamada al modelo
    respuesta_ia = llamar_gemini(pregunta_usuario)
    insertar_texto(f"Asistente: {respuesta_ia}")

boton_enviar = tk.Button(frame_entrada, text="Enviar", command=enviar_consulta, font=("Arial", 10, "bold"))
boton_enviar.pack(side=tk.RIGHT, padx=6)

def limpiar_chat():
    area_chat.config(state='normal')
    area_chat.delete(1.0, tk.END)
    area_chat.config(state='disabled')
    insertar_texto("Asistente: ¡Hola! Bienvenido al Asistente de DonBald. Escribe tu pregunta abajo.")
    insertar_texto(f"[Modelo en uso: {MODEL_NAME}]")

boton_limpiar = tk.Button(frame_entrada, text="Limpiar", command=limpiar_chat, font=("Arial", 10))
boton_limpiar.pack(side=tk.RIGHT, padx=6)

ventana.mainloop()
