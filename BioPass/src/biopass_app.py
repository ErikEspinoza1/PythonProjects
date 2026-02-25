import tkinter as tk
from tkinter import messagebox, Label
import cv2
from PIL import Image, ImageTk # Necesario para mostrar video en Tkinter
from src.usuario_dao import UsuarioDAO
from src.utils.camera_utils import CameraUtils

class BioPassApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BioPass DAO - Sistema de Acceso Biométrico")
        self.root.geometry("800x600")

        # 1. Inicializamos la cámara con OpenCV
        self.cap = cv2.VideoCapture(0)
        
        # 2. Panel para mostrar el video
        self.video_label = Label(self.root)
        self.video_label.pack(pady=20)

        # 3. Campo de texto para el nombre (Solo para registro)
        self.entry_nombre = tk.Entry(self.root, font=("Arial", 14))
        self.entry_nombre.pack(pady=5)
        self.entry_nombre.insert(0, "Escribe tu nombre aquí")

        # 4. Botones de Acción
        # Botón REGISTRAR: Guarda foto y cara en la BD
        btn_registro = tk.Button(self.root, text="📷 Registrar Usuario", 
                                 command=self.registrar_usuario, 
                                 bg="#4CAF50", fg="white", font=("Arial", 12))
        btn_registro.pack(pady=10, fill='x', padx=50)

        # Botón LOGIN: Descarga fotos, entrena y predice
        btn_login = tk.Button(self.root, text="🔓 Iniciar Sesión (Reconocimiento)", 
                              command=self.login_usuario, 
                              bg="#2196F3", fg="white", font=("Arial", 12))
        btn_login.pack(pady=10, fill='x', padx=50)

        # Variable para guardar el último frame (foto actual)
        self.frame_actual = None
        
        # Iniciamos el bucle de video
        self.actualizar_video()

    def actualizar_video(self):
        """Lee la cámara frame a frame y la muestra en la ventana"""
        ret, frame = self.cap.read()
        if ret:
            self.frame_actual = frame # Guardamos copia para usar al hacer clic
            
            # Convertimos color de BGR (OpenCV) a RGB (Tkinter)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        
        self.root.after(10, self.actualizar_video)

    def registrar_usuario(self):
        """Flujo: Captura -> Detecta -> Bytes -> DAO"""
        nombre = self.entry_nombre.get()
        if not nombre or nombre == "Escribe tu nombre aquí":
            messagebox.showwarning("Aviso", "Por favor, escribe un nombre.")
            return

        if self.frame_actual is None: return

        # 1. Detectar rostro y recortar
        cara_recortada, coords = CameraUtils.detectar_rostro(self.frame_actual)
        
        if cara_recortada is None:
            messagebox.showerror("Error", "No se detecta ningún rostro. Acércate más.")
            return

        # 2. Convertir ambas imágenes a Bytes (BLOBs)
        foto_bytes = CameraUtils.convertir_a_bytes(self.frame_actual)
        cara_bytes = CameraUtils.convertir_a_bytes(cara_recortada)

        # 3. Llamar al DAO (El traductor SQL)
        exito = UsuarioDAO.registrar_usuario(nombre, foto_bytes, cara_bytes)

        if exito:
            messagebox.showinfo("Éxito", f"Usuario '{nombre}' registrado en PostgreSQL.")
        else:
            messagebox.showerror("Error", "No se pudo guardar en la base de datos.")

    def login_usuario(self):
        """Flujo: DAO -> Entrenar -> Predecir"""
        if self.frame_actual is None: return

        # 1. Detectar rostro actual
        cara_recortada, coords = CameraUtils.detectar_rostro(self.frame_actual)
        if cara_recortada is None:
            messagebox.showerror("Error", "No veo ninguna cara para analizar.")
            return

        # 2. Obtener datos de entrenamiento desde la BD (Lazy Training)
        print("📥 Descargando usuarios de la BD...")
        usuarios = UsuarioDAO.obtener_todos()
        
        if not usuarios:
            messagebox.showwarning("Vacío", "No hay usuarios registrados en la BD.")
            return

        # 3. Entrenar modelo en RAM y Predecir
        print(f"🧠 Entrenando con {len(usuarios)} usuarios...")
        nombre_predicho, confianza = CameraUtils.entrenar_y_predecir(usuarios, cara_recortada)

        # 4. Mostrar resultado
        if nombre_predicho != "Desconocido":
            mensaje = f"¡Bienvenido, {nombre_predicho}!\nConfianza: {round(confianza, 2)}"
            tipo_msg = "info"
        else:
            mensaje = "Acceso Denegado: Usuario no reconocido."
            tipo_msg = "error"
            
        messagebox.showinfo("Resultado Biométrico", mensaje)

    def cerrar(self):
        self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BioPassApp(root)
    root.protocol("WM_DELETE_WINDOW", app.cerrar)
    root.mainloop()