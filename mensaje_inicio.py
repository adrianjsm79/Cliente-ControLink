import tkinter as tk
import os

def mostrar_mensaje_inicio():
    ventana = tk.Tk()
    ventana.overrideredirect(True)
    ventana.attributes("-topmost", True)

    # Configuración de transparencia
    ventana.config(bg='pink')
    ventana.wm_attributes('-transparentcolor', 'pink')

    # Tamaño y posición
    ancho, alto = 350, 80
    x = (ventana.winfo_screenwidth() - ancho) // 2
    y = (ventana.winfo_screenheight() - alto) // 2
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

    # Canvas con fondo transparente
    canvas = tk.Canvas(ventana, width=ancho, height=alto, bg='pink', highlightthickness=0)
    canvas.pack()

    # Dibujar rectángulo redondeado
    def dibujar_rect_redondeado(x1, y1, x2, y2, r, **kwargs):
        canvas.create_arc(x1, y1, x1 + 2*r, y1 + 2*r, start=90, extent=90, style='pieslice', **kwargs)
        canvas.create_arc(x2 - 2*r, y1, x2, y1 + 2*r, start=0, extent=90, style='pieslice', **kwargs)
        canvas.create_arc(x1, y2 - 2*r, x1 + 2*r, y2, start=180, extent=90, style='pieslice', **kwargs)
        canvas.create_arc(x2 - 2*r, y2 - 2*r, x2, y2, start=270, extent=90, style='pieslice', **kwargs)
        canvas.create_rectangle(x1 + r, y1, x2 - r, y2, **kwargs)
        canvas.create_rectangle(x1, y1 + r, x2, y2 - r, **kwargs)

    dibujar_rect_redondeado(0, 0, ancho, alto, r=35, fill="#000000")

    # Cargar imagen PNG
    icon_path = os.path.join(os.path.dirname(__file__), "short.png")
    if os.path.exists(icon_path):
        imagen = tk.PhotoImage(file=icon_path)
        icono = tk.Label(ventana, image=imagen, bg="#000000")
        icono.image = imagen  # evitar que se elimine de memoria
        icono.place(x=20, y=20)
    else:
        print("image not found")

    # Texto
    label = tk.Label(
        ventana,
        text="Cliente PACO PC corriendo...",
        font=("Segoe UI", 12, "bold"),
        bg="#000000",
        fg="white",
        anchor="w",
        justify="left"
    )
    label.place(x=70, y=25)

    # Fade-in
    ventana.attributes("-alpha", 0.0)
    def fade_in(opacidad=0.0):
        if opacidad < 0.85:
            ventana.attributes("-alpha", opacidad)
            ventana.after(30, lambda: fade_in(opacidad + 0.05))
        else:
            ventana.attributes("-alpha", 0.85)
            ventana.after(3000, ventana.destroy)
    fade_in()
    ventana.mainloop()

if __name__ == "__main__":
    mostrar_mensaje_inicio()
