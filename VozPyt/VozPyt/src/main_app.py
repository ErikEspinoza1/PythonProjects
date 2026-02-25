import tkinter as tk
from tkinter import messagebox, scrolledtext
import time
from datetime import datetime, timedelta
from src.auth_dao import AuthDAO
from src.voice_service import VoiceService

class VoiceAuditApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VoiceAudit - Acceso por Voz (JSONB)")
        self.root.geometry("650x600")
        self.root.configure(padx=20, pady=20)

        # 1. Campo de Usuario
        tk.Label(self.root, text="Nombre de Usuario:", font=("Arial", 12)).pack(pady=5)
        self.entry_username = tk.Entry(self.root, font=("Arial", 14))
        self.entry_username.pack(pady=5)

        # 2. Botones de Acción Principal
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        btn_registro = tk.Button(btn_frame, text="Registrar Frase de Paso", 
                                 command=self.registrar_usuario, bg="#4CAF50", fg="white", font=("Arial", 11))
        btn_registro.grid(row=0, column=0, padx=10)

        btn_login = tk.Button(btn_frame, text="Iniciar Sesión (Voz)", 
                              command=self.login_usuario, bg="#2196F3", fg="white", font=("Arial", 11))
        btn_login.grid(row=0, column=1, padx=10)

        # 3. Separador y Botón de Auditoría
        tk.Frame(self.root, height=2, bd=1, relief="sunken").pack(fill="x", pady=15)
        
        btn_auditoria = tk.Button(self.root, text="Ver Auditoría Crítica", 
                                  command=self.mostrar_auditoria, bg="#FF9800", fg="white", font=("Arial", 11))
        btn_auditoria.pack(pady=5)

        # 4. Panel de Texto para la Auditoría
        self.text_auditoria = scrolledtext.ScrolledText(self.root, width=70, height=12, font=("Consolas", 10))
        self.text_auditoria.pack(pady=10)

        self.MAX_INTENTOS = 3

    def registrar_usuario(self):
        """Flujo de Registro: Captura -> Confirma -> DAO"""
        username = self.entry_username.get().strip()
        if not username:
            messagebox.showwarning("Aviso", "Introduce un nombre de usuario.")
            return

        # Verificamos si ya existe (para no sobreescribir)
        if AuthDAO.obtener_usuario(username):
            messagebox.showerror("Error", "El usuario ya existe. Usa Iniciar Sesión.")
            return

        # 1. Usamos el Facade para escuchar [cite: 101]
        self.root.config(cursor="watch")
        self.root.update()
        texto, confianza, estado = VoiceService.capturar_voz()
        self.root.config(cursor="")

        # Manejo de errores del micrófono
        if not texto:
            messagebox.showerror("Error de Audio", estado)
            return

        # 2. Confirmación del usuario [cite: 102]
        msg = f"He entendido: '{texto}'\n\n¿Es correcta esta frase secreta?"
        if messagebox.askyesno("Confirmar Frase", msg):
            # 3. Preparamos el JSON del log inicial [cite: 104, 107]
            log_data = {
                "status": "OK",
                "evento": "registro",
                "confianza": confianza,
                "frase_registrada": texto
            }
            # 4. Guardamos en BD [cite: 103]
            if AuthDAO.registrar_usuario(username, texto, log_data):
                messagebox.showinfo("Éxito", f"Usuario '{username}' registrado correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo registrar en la base de datos.")

    def login_usuario(self):
        """Flujo de Login: BD -> Captura -> Compara -> Actualiza JSONB"""
        username = self.entry_username.get().strip()
        if not username:
            messagebox.showwarning("Aviso", "Introduce un nombre de usuario.")
            return

        # 1. Buscar usuario en la BD
        user_data = AuthDAO.obtener_usuario(username)
        if not user_data:
            messagebox.showerror("Error", "Usuario no encontrado.")
            return

        user_id, frase_bd, intentos_fallidos, bloqueado_hasta = user_data

        # 2. Comprobar si está bloqueado [cite: 116]
        if bloqueado_hasta and bloqueado_hasta > datetime.now():
            tiempo_restante = (bloqueado_hasta - datetime.now()).seconds // 60
            messagebox.showerror("Bloqueado", f"Cuenta bloqueada. Intenta en {tiempo_restante + 1} minutos.")
            return

        # 3. Capturar voz y medir latencia
        self.root.config(cursor="watch")
        self.root.update()
        
        inicio_tiempo = time.time()
        texto, confianza, estado = VoiceService.capturar_voz() # Facade [cite: 114]
        latencia = round(time.time() - inicio_tiempo, 2)
        
        self.root.config(cursor="")

        # Si hubo un error técnico con el micrófono [cite: 110, 111]
        if not texto:
            log_error = {"status": "ERROR", "motivo": estado, "latencia_s": latencia}
            AuthDAO.registrar_log(user_id, log_error)
            messagebox.showerror("Error de Audio", estado)
            return

        # 4. Lógica de Validación
        if texto == frase_bd:
            # ÉXITO: Reiniciamos intentos y guardamos log [cite: 117]
            AuthDAO.actualizar_intentos(user_id, 0, None)
            log_exito = {"status": "OK", "confianza": confianza, "latencia_s": latencia}
            AuthDAO.registrar_log(user_id, log_exito)
            messagebox.showinfo("Bienvenido", f"Acceso concedido.\nConfianza de la IA: {confianza*100:.1f}%")
        else:
            # FALLO: Restamos intentos y bloqueamos si es necesario [cite: 115, 116]
            intentos_fallidos += 1
            intentos_restantes = self.MAX_INTENTOS - intentos_fallidos
            
            if intentos_restantes <= 0:
                # Bloqueo por 5 minutos
                tiempo_desbloqueo = datetime.now() + timedelta(minutes=5)
                AuthDAO.actualizar_intentos(user_id, intentos_fallidos, tiempo_desbloqueo)
                estado_bloqueo = "BLOQUEADO"
            else:
                AuthDAO.actualizar_intentos(user_id, intentos_fallidos, None)
                estado_bloqueo = "ACTIVO"

            # Preparamos el JSON dinámico de fallo [cite: 109]
            log_fallo = {
                "status": "FAIL", 
                "frase_intentada": texto, 
                "intentos_restantes": max(0, intentos_restantes),
                "estado_cuenta": estado_bloqueo
            }
            AuthDAO.registrar_log(user_id, log_fallo)
            messagebox.showwarning("Acceso Denegado", f"Frase incorrecta. Entendí: '{texto}'.\nIntentos restantes: {max(0, intentos_restantes)}")

    def mostrar_auditoria(self):
        """Descarga los registros críticos del JSONB y los muestra [cite: 122, 123, 124]"""
        registros = AuthDAO.obtener_auditoria_critica()
        
        self.text_auditoria.delete(1.0, tk.END) # Limpiar panel
        self.text_auditoria.insert(tk.END, "--- REGISTROS DE AUDITORÍA CRÍTICA (JSONB) ---\n\n")
        
        if not registros:
            self.text_auditoria.insert(tk.END, "No hay eventos críticos (Fallos o baja confianza).")
            return

        for reg in registros:
            username = reg[0]
            status = reg[1]
            json_data = reg[2] # El diccionario completo guardado en PostgreSQL
            
            linea = f"Usuario: {username} | Estado: {status} | Datos JSON: {json_data}\n"
            self.text_auditoria.insert(tk.END, linea)

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceAuditApp(root)
    root.mainloop()