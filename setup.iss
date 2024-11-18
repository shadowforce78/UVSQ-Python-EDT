[Setup]
AppName=UVSQ-EDT-APP
AppVersion=1.0
DefaultDirName={pf}\UVSQ-EDT-APP
OutputDir=dist
SetupIconFile=logo.ico

[Files]
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Crée une entrée dans le menu Démarrer
Name: "{group}\UVSQ-EDT-APP"; Filename: "{app}\main.exe"; WorkingDir: "{app}"
; Ajoute une option pour désinstaller depuis le menu Démarrer
Name: "{group}\Désinstaller UVSQ-EDT-APP"; Filename: "{uninstallexe}"