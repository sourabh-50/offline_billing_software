; Inno Setup Script for Omsai Billing Software
; ScaleAd Digital Growth Agency

[Setup]
AppId={{8B3A8B9E-7A1B-4C9D-9E2A-6C3D55AA332F}
AppName=Anuj Billing Software
AppVersion=1.1.0
AppPublisher=ScaleAd
AppPublisherURL=https://scalead.in
DefaultDirName={autopf}\Omsai Billing Software
DefaultGroupName=Omsai Billing Software
OutputDir=dist\Installers
OutputBaseFilename=BillingSystem_Setup
SetupIconFile=assets\app_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; NOTE: Change the Source path below to match your client's built folder (e.g., dist\\Client_Packages\\omsai\\*)
Source: "dist\\Client_Packages\\omsai\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Omsai Billing Software"; Filename: "{app}\Omsai Billing Software.exe"
Name: "{autodesktop}\Omsai Billing Software"; Filename: "{app}\Omsai Billing Software.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Omsai Billing Software.exe"; Description: "{cm:LaunchProgram,Omsai Billing Software}"; Flags: nowait postinstall skipifsilent
