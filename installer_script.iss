; -- installer_script.iss --
; Professional Inno Setup Script for Omsai Billing Software

[Setup]
AppName=Omsai Billing Software
AppVersion=1.0.0
DefaultDirName={autopf}\Omsai Billing Software
DefaultGroupName=Omsai Billing Software
UninstallDisplayIcon={app}\Omsai Billing Software.exe
Compression=lzma2
SolidCompression=yes
OutputDir=userdocs:Inno Setup Outputs
OutputBaseFilename=Omsai_Billing_Setup
SetupIconFile=assets\app_icon.ico
PrivilegesRequired=admin

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; IMPORTANT: This assumes you have already run 'pyinstaller MobileShopBiller.spec'
Source: "dist\Omsai Billing Software\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Omsai Billing Software"; Filename: "{app}\Omsai Billing Software.exe"
Name: "{autodesktop}\Omsai Billing Software"; Filename: "{app}\Omsai Billing Software.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Omsai Billing Software.exe"; Description: "{cm:LaunchProgram,Omsai Billing Software}"; Flags: nowait postinstall skipifsilent
