# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 项目根目录
root_dir = os.path.abspath('.')

# 分析项目依赖
a = Analysis(
    ['main.py'],  # 主程序入口
    pathex=[root_dir],  # 项目根目录
    binaries=[],
    datas=[
        # 包含配置文件
        (os.path.join(root_dir, 'config.json'), '.'),
        # 包含其他可能的JSON文件
        (os.path.join(root_dir, '*.json'), '.'),
        # 包含资源文件
        (os.path.join(root_dir, 'resources'), 'resources'),
        # 包含UI相关文件
        (os.path.join(root_dir, 'ui'), 'ui'),
        (os.path.join(root_dir, 'core'), 'core'),
        (os.path.join(root_dir, 'utils'), 'utils')
    ],
    hiddenimports=[
        # 显式指定可能被动态导入的模块
        'pandas',
        'openpyxl',
        'xlrd',
        'PyQt5',
        'PyQt5.QtWidgets',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'json',
        're',
        'concurrent.futures'
    ] + collect_submodules('core') + collect_submodules('ui') + collect_submodules('utils'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 生成PYZ文件
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 生成主程序EXE（无控制台窗口）
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LogAnalyzer',  # 可执行程序名称
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 使用UPX压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示终端窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(root_dir, 'resources', 'app_icon.ico')  # 指定图标
)

# 收集所有依赖文件到dist目录
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,  # 使用UPX压缩
    upx_exclude=[],
    name='LogAnalyzer',  # 输出目录名称
    distpath=root_dir,  # 输出到项目根目录
)
