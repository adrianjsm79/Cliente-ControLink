[Setup]
AppName=ControLink ClientPC
AppVersion=1.5
DefaultDirName={localappdata}\ControLink_ClientPC
DisableProgramGroupPage=yes
OutputDir=.
OutputBaseFilename=Instalador ControLink ClientPC
Compression=lzma
SolidCompression=yes
SetupIconFile=icon.ico
LicenseFile=aviso.txt

[Files]
Source: "clientepython.exe"; DestDir: "{app}"; Flags: ignoreversion

[Tasks]
Name: "autostart"; Description: "Ejecutar Cliente al iniciar Windows"; GroupDescription: "Opciones de acceso directo"; Flags: checkedonce
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Opciones de acceso directo"; Flags: checkedonce

[Icons]
Name: "{userstartup}\PACO ClientPC"; Filename: "{app}\clientepython.exe"; WorkingDir: "{app}"; Tasks: autostart
Name: "{userdesktop}\PACO ClientPC"; Filename: "{app}\clientepython.exe"; WorkingDir: "{app}"; IconFilename: "{app}\clientepython.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\clientepython.exe"; Description: "Iniciar cliente ahora"; Flags: nowait postinstall skipifsilent
