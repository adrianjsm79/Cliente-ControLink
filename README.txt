EJECUTE 

pip install -r requirements

luego

pyinstaller --onefile --noconsole --icon=icon.ico --add-data "icon.ico;." --add-data "short.png;." --add-data "version.txt;." --add-data "noti.mp3;."  clientepython.py

EN LA CONSOLA para crear el .exe, 
luego compile el archivo "instalador.iss"  para crear un instalador con 
inno setup



