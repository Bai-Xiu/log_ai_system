# package.spec
import sys
import os
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis
from PyInstaller.building.datastruct import Tree

# 项目根目录
root_dir = os.path.abspath('.')

# 分析项目依赖
a = Analysis(
    ['main.py'],  # 程序入口
    pathex=[root_dir],
    binaries=[],
    datas=[
        (os.path.join(root_dir, 'resources'), 'resources'),  # 资源文件
        (os.path.join(root_dir, 'config.json'), '.')         # 配置文件
    ],
    hiddenimports=[
        'pandas', 'numpy', 'openpyxl', 'PyQt5', 
        'PyQt5.QtWidgets', 'PyQt5.QtCore', 'PyQt5.QtGui',
        'openai'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[  # 排除不需要的库，减小体积
        'matplotlib', 'tkinter', 'scipy', 'sklearn',
        'torch', 'tensorflow', 'keras', 'cv2',
        'PIL', 'xlwt', 'pytest', 'jupyter'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 压缩处理
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 生成可执行文件（无控制台窗口）
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='log_ai_system',  # 可执行文件名称
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 启用UPX压缩
    console=False,  # 不显示控制台
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(root_dir, 'resources', 'app_icon.ico')  # 图标文件
)

# 收集所有文件并按文件夹结构输出
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='log_ai_system',  # 输出文件夹名称
)