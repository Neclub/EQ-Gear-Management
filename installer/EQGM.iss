; EQ Gear Management — Inno Setup installer (EQLog Parser–style layout).
; Compile with ISCC.exe after Nuitka builds dist\pyinstaller_gui.dist\
;
; Version is passed from build_exe.bat:
;   ISCC.exe /DMyAppVersion=1.35.11 installer\EQGM.iss

#ifndef MyAppVersion
  #error MyAppVersion must be defined (e.g. ISCC /DMyAppVersion=1.35.11)
#endif

#define MyAppName "EQ Gear Management"
#define MyAppPublisher "Lubworks"
#define MyAppURL "https://github.com/Neclub/EQ-Gear-Management"
#define MyAppExeName "EQGM.exe"
#define MyReleaseDir "..\dist\pyinstaller_gui.dist"
#define MyIconFile "..\src\inventory_parser\assets\eq-icon.ico"

[Setup]
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible
AppId={{69213E35-8BA0-4151-A501-6A71CE54E716}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={commonpf}\{#MyAppName}
DisableDirPage=no
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=EQGM-install-{#MyAppVersion}
SetupIconFile={#MyIconFile}
UninstallDisplayIcon={app}\{#MyAppExeName}
MinVersion=10.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#MyReleaseDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
