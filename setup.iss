; setup.iss
[Setup]
AppName=信息安全日志AI分析系统
AppVersion=1.0
DefaultDirName={pf}\log_ai_system
DefaultGroupName=log_ai_system
OutputDir=D:\log_ai_system\installer
OutputBaseFilename=log_ai_system_setup
SetupIconFile=D:\log_ai_system\resources\app_icon.ico
Compression=lzma2
SolidCompression=yes

[Languages]
Name: "chinese"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "D:\log_ai_system\dist\log_ai_system\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\信息安全日志AI分析系统"; Filename: "{app}\log_ai_system.exe"
Name: "{commondesktop}\信息安全日志AI分析系统"; Filename: "{app}\log_ai_system.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加任务:"

[Run]
Filename: "{app}\log_ai_system.exe"; Description: "运行信息安全日志AI分析系统"; Flags: nowait postinstall skipifsilent