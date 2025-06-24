import os   #operaciones del sistema operativo
import time   #para el (sleep) y medir tiempo
import socket   #obtiene información de red del equipo (IP y nombre)
import requests   #para hacer peticiones HTTP al servidor intermedio
import threading   #ejecutar funciones en paralelo (los hilos)
from flask import Flask, request   #flask crea una API local
from pystray import Icon, MenuItem, Menu   #es para poner el icono en la barra de tareas xd
from PIL import Image   #permite manejar imágenes (especificamente el icono de la barra de tareas)
import sys   #Acceso a la info del sistema, rutas de ejecución, etc
from mensaje_inicio import mostrar_mensaje_inicio  #el mensaje de inicio :v
from notificacion import mostrar_notificacion_deluxe, reproducir_sonido  #llama a las funciones de mostrar notificación y sonido


BASE_PATH = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
RUTA_ICONO = os.path.join(BASE_PATH, "icon.ico")    #esto sirve para definir la ruta tanto del icono(notificacion)como
RUTA_SONIDO = os.path.join(BASE_PATH, "noti.mp3")   #del sonido de la noti, para cuando se cree el .exe

app = Flask(__name__) #variable del servidor http local

SERVIDOR_CENTRAL = "https://servidor-controlpc.onrender.com" #variable del url del servidor intermedio

def obtener_nombre_equipo():   #esta funcion utilitaria obtiene el nombre del equipo
    return socket.gethostname() 

def obtener_ip_local():
    try:
        # Crea un socket UDP y se conecta a Google DNS
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            return ip
    except Exception as e:
        print(f"Error al obtener IP local: {e}")
        # Intenta obtener IP por nombre del host
        try:
            ip = socket.gethostbyname(socket.gethostname())
            if ip.startswith("127."):
                raise Exception("IP es localhost")
            return ip
        except:
            return "127.0.0.1"

def obtener_ruta_icono(nombre_archivo):
    #Devuelve la ruta absoluta del ícono, compatible con ejecutables
    if getattr(sys, 'frozen', False):
        ruta_base = sys._MEIPASS
    else:
        ruta_base = os.path.dirname(__file__)
    return os.path.join(ruta_base, nombre_archivo)

def registrar_en_servidor_central():
    #envia el nombre y la ip (o localhost) del equipo al servidor intermedio para dejar constancia en un json 
    #de que el ciente de esta pc esta activo para recibir comandos.
    nombre = obtener_nombre_equipo()
    ip = obtener_ip_local()
    try:
        respuesta = requests.post(f"{SERVIDOR_CENTRAL}/registrar", json={
            "nombre": nombre,
            "ip": ip
        }, timeout=5) #timeout de 5 segundos para evitar bloqueos si el servidor no responde
        if respuesta.status_code == 200:
            #si la respuesta es correcta imprime el mensaje de texto en la consola
            #y muestra una notificación en la bandeja del sistema
            print(f"Registrado como '{nombre}' con IP '{ip}' en el servidor central")
        else:
            print(f"Error al registrar: {respuesta.text}")
    except requests.RequestException as e:
        print(f"No se pudo conectar al servidor central: {e}")

def actualizar_actividad_periodicamente():
    #envia el nombre del equipo al servidor intermedio cada 10 segundos
    #para que el servidor sepa que el cliente sigue activo
    nombre = obtener_nombre_equipo() 
    while True:
        try:
            requests.post(f"{SERVIDOR_CENTRAL}/actualizar_actividad/{nombre}", timeout=5)
        except requests.RequestException:
            pass
        time.sleep(10)

def obtener_ruta_descarga():
    #se define la ruta donde se descargaran los archivos recibidos 
    return os.path.join(os.path.expanduser("~"), "Downloads", "Recibidos")

def procesar_comando_descargar(nombre_archivo):
    #recibe el nombre del archivo a descargar y crea la carpeta de descargas si no existe
    ruta_descargas = obtener_ruta_descarga()
    os.makedirs(ruta_descargas, exist_ok=True)
    ruta_destino = os.path.join(ruta_descargas, nombre_archivo)

    try:
        #intenta descargar el archivo del servidor intermedio usando streaming
        archivo_respuesta = requests.get(f"{SERVIDOR_CENTRAL}/descargas/{nombre_archivo}", stream=True, timeout=30)
        if archivo_respuesta.status_code == 200:
            with open(ruta_destino, "wb") as f:
                for chunk in archivo_respuesta.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"Archivo guardado en {ruta_descargas}")
            #muestra una notificación en la bandeja del sistema con el nombre del archivo descargado
            #y reproduce un sonido de notificación
            mostrar_notificacion_deluxe(mensaje=nombre_archivo)
            reproducir_sonido()
        else:
            print(f"Error al descargar archivo: {archivo_respuesta.status_code}")
    except requests.RequestException as e:
        print(f"Error de red al descargar archivo: {e}")

def verificar_comandos():
    #consulta periódicamente al servidor si hay comandos pendientes para el equipo
    nombre = obtener_nombre_equipo()
    while True:
        try:
            respuesta = requests.get(f"{SERVIDOR_CENTRAL}/comando/{nombre}/pendiente", timeout=5)
            if respuesta.status_code == 200:
                data = respuesta.json() #obtiene la respuesta en formato json
                accion = data.get("accion")
                if accion == "apagar":
                    print("Comando recibido: Apagar")
                    os.system("shutdown /s /t 0") 
                elif accion == "reiniciar":
                    print("Comando recibido: Reiniciar")
                    os.system("shutdown /r /t 0")
                elif accion == "bloquear":
                    print("Comando recibido: Bloquear")
                    os.system("rundll32.exe user32.dll,LockWorkStation")
                elif accion and accion.startswith("descargar::"): 
                    nombre_archivo = accion.split("::", 1)[1] #extrae el nombre del archivo del comando
                    procesar_comando_descargar(nombre_archivo)
        except requests.RequestException as e:
            print(f"Error al consultar comando: {e}")
        time.sleep(5)
        #espera 5 segundos antes de volver a consultar el servidor

@app.route('/ping') # Ruta para verificar si el servidor está activo
def ping():
    nombre = obtener_nombre_equipo()
    return f"Servidor activo: {nombre}", 200

def cerrar(icono, item):  #quita el icono de la barra de tareas y cierra el programa
    icono.stop()
    os._exit(0) #cierra todos los procesos al cerrrar el icono

def crear_icono_bandeja(): #Crea el icono en la barra de tareas con opción
                           #de salir del programa. Usa pystray y PIL.
    ruta_icono = obtener_ruta_icono("short.png")
    image = Image.open(ruta_icono)
    menu = Menu(MenuItem("Salir", cerrar)) #abre un menu con la libreria de pystray
    icono = Icon("ClientPC", image, "Controlink-ClientPC", menu) 
    icono.run()

def main():
    mostrar_mensaje_inicio()
    registrar_en_servidor_central()
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000), daemon=True).start()
    threading.Thread(target=verificar_comandos, daemon=True).start()
    threading.Thread(target=actualizar_actividad_periodicamente, daemon=True).start()
    threading.Thread(target=crear_icono_bandeja, daemon=True).start()
    # Espera indefinidamente para evitar que el hilo principal termine
    threading.Event().wait()

if __name__ == '__main__':
    main()
