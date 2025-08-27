; LogAnalyzer_Setup.iss
[Setup]
AppName=信息安全日志AI分析系统
AppVersion=1.0.0
AppPublisher=YourName
DefaultDirName={pf}\LogAnalyzer
DefaultGroupName=LogAnalyzer
OutputDir=./installer
OutputBaseFilename=LogAnalyzer_Setup
SetupIconFile=./resources/app_icon.ico
UninstallDisplayIcon={app}\LogAnalyzer.exe
Compression=lzma2
SolidCompression=yes

[Files]
; 复制dist/LogAnalyzer下的所有文件到安装目录
Source: "dist\LogAnalyzer\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
; 创建桌面快捷方式
Name: "{commondesktop}\信息安全日志AI分析系统"; Filename: "{app}\LogAnalyzer.exe"; WorkingDir: "{app}"
; 创建开始菜单快捷方式
Name: "{group}\信息安全日志AI分析系统"; Filename: "{app}\LogAnalyzer.exe"; WorkingDir: "{app}"
Name: "{group}\卸载"; Filename: "{uninstallexe}"

[Run]
; 安装完成后运行程序
Filename: "{app}\LogAnalyzer.exe"; Description: "启动信息安全日志AI分析系统"; Flags: nowait postinstall skipifsilent