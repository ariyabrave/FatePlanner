#define MyAppName "FatePlanner"

#ifndef MyAppVersion
  #define MyAppVersion "0.1.0"
#endif

#define MyAppPublisher "ariyabrave"
#define MyAppURL "https://github.com/ariyabrave/FatePlanner"
#define MyAppExeName "FatePlanner.exe"


[Setup]

AppId={{74BA735B-1ABB-4DD5-AE96-D6A45C33EE6A}

AppName={#MyAppName}
AppVersion={#MyAppVersion}

AppVerName={#MyAppName} {#MyAppVersion}

AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases

DefaultDirName={autopf}\FatePlanner
DefaultGroupName=FatePlanner

AllowNoIcons=yes
DisableProgramGroupPage=yes

OutputDir=..\..\dist\installer

OutputBaseFilename=FatePlanner-Windows-Setup-v{#MyAppVersion}

SetupIconFile=FatePlanner.ico

UninstallDisplayIcon={app}\FatePlanner.exe

Compression=lzma2
SolidCompression=yes

WizardStyle=modern

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

PrivilegesRequired=admin

CloseApplications=yes
RestartApplications=no

VersionInfoVersion={#MyAppVersion}.0
VersionInfoCompany=FatePlanner
VersionInfoDescription=FatePlanner Personal Planner
VersionInfoProductName=FatePlanner
VersionInfoProductVersion={#MyAppVersion}


[Languages]

Name: "english"; \
    MessagesFile: "compiler:Default.isl"


[Tasks]

Name: "desktopicon"; \
    Description: "Create a desktop shortcut"; \
    GroupDescription: "Additional shortcuts:"; \
    Flags: unchecked


[Files]

Source: "..\..\dist\FatePlanner\*"; \
    DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs


[Icons]

Name: "{group}\FatePlanner"; \
    Filename: "{app}\FatePlanner.exe"; \
    WorkingDir: "{app}"

Name: "{autodesktop}\FatePlanner"; \
    Filename: "{app}\FatePlanner.exe"; \
    WorkingDir: "{app}"; \
    Tasks: desktopicon


[Run]

Filename: "{app}\FatePlanner.exe"; \
    Description: "Launch FatePlanner"; \
    Flags: nowait postinstall skipifsilent