import tkinter as tk
import threading
import os
import time
import webbrowser
from PIL import Image, ImageTk
import pygame
import sys

# CONFIGURACIÓN
RUTA_DESCARGA = os.path.join(os.path.expanduser("~"), "Downloads", "Recibidos")
BASE_PATH = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))) # Ruta base del script
RUTA_ICONO = os.path.join(BASE_PATH, "icon.ico") # Ruta al icono de la notificación
RUTA_SONIDO = os.path.join(BASE_PATH, "noti.mp3") # Ruta al sonido de notificación
DURACION = 7  # Duración de la notificación
ANIM_FRAMES=35 # Número de frames para la animación

def abrir_carpeta():
    os.makedirs(RUTA_DESCARGA, exist_ok=True)
    webbrowser.open(RUTA_DESCARGA)

def reproducir_sonido():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(RUTA_SONIDO)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"[sonido] Error: {e}")

def animar_entrada(noti, x, y_final):
    y_inicio = y_final + 100
    paso_y = (y_inicio - y_final) / ANIM_FRAMES
    paso_alpha = 0.85 / ANIM_FRAMES

    for i in range(ANIM_FRAMES):
        y = int(y_inicio - paso_y * i)
        alpha = paso_alpha * i
        noti.geometry(f"+{x}+{y}")
        noti.attributes("-alpha", alpha)
        time.sleep(0.015)

def animar_salida(noti, x, y_inicio):
    paso_y = 100 / ANIM_FRAMES
    paso_alpha = 0.85 / ANIM_FRAMES

    for i in range(ANIM_FRAMES):
        y = int(y_inicio + paso_y * i)
        alpha = max(0, 0.85 - paso_alpha * i)
        noti.geometry(f"+{x}+{y}")
        noti.attributes("-alpha", alpha)
        time.sleep(0.015)

    if noti.winfo_exists():
        noti.destroy()

def mostrar_en_tk(titulo, mensaje):
    noti = tk.Toplevel()
    noti.overrideredirect(True)
    noti.attributes("-topmost", True)
    noti.attributes("-alpha", 0.0)  # Comienza transparente
    noti.configure(bg="black")

    # Posición: parte inferior derecha
    width, height = 350, 120
    x = noti.winfo_screenwidth() - width - 10
    y_final = noti.winfo_screenheight() - height - 50
    y_inicial = y_final + 100
    noti.geometry(f"{width}x{height}+{x}+{y_inicial}")

    # Bordes suaves
    canvas = tk.Canvas(noti, bg="black", highlightthickness=0)
    canvas.place(relwidth=1, relheight=1)

    # Icono
    try:
        img = Image.open(RUTA_ICONO).resize((60, 60), Image.Resampling.LANCZOS)
        icon = ImageTk.PhotoImage(img)
        canvas.create_image(50, 50, anchor="center", image=icon)
        noti.icon_ref = icon  # Mantener una referencia al icono
    except Exception as e:
        print(f"[icono] Error: {e}")

    # Texto
    tk.Label(noti, text=titulo, font=("Segoe UI", 12, "bold"),
             fg="white", bg="black", anchor="w", justify="left").place(x=80, y=15, width=250)

    tk.Label(noti, text=mensaje, font=("Segoe UI", 10),
             fg="white", bg="black", anchor="w", justify="left", wraplength=250).place(x=80, y=40, width=250)

    # Botón
    tk.Button(noti, text="Abrir carpeta", command=lambda: [abrir_carpeta(), noti.destroy()],
              bg="#85C8F2", fg="black", border=0, font=("Segoe UI", 10, "bold"),
              relief="flat", cursor="hand2").place(x=80, y=75, width=120, height=25)

 # Animación de entrada
    threading.Thread(target=animar_entrada, args=(noti, x, y_final), daemon=True).start()

    # Cierre automático con animacion
    def cerrar_con_animacion():
        time.sleep(DURACION)
        if noti.winfo_exists():
            animar_salida(noti, x, y_final)

    threading.Thread(target=cerrar_con_animacion, daemon=True).start()

def mostrar_notificacion_deluxe(titulo="Archivo recibido", mensaje=""):
    def iniciar_tk():
        root = tk.Tk()
        root.withdraw()
        mostrar_en_tk(titulo, mensaje)
        root.mainloop()
    threading.Thread(target=iniciar_tk, daemon=True).start()
