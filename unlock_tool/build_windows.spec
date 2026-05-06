# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

ROOT_DIR = Path(os.getcwd()).resolve()

binaries = []
datas = []

# Only add files/directories that exist
if (ROOT_DIR / 'devices.json').exists():
    datas.append((str(ROOT_DIR / 'devices.json'), '.'))
if (ROOT_DIR / 'drivers').exists():
    datas.append((str(ROOT_DIR / 'drivers'), 'drivers'))
if (ROOT_DIR / 'assets').exists():
    datas.append((str(ROOT_DIR / 'assets'), 'assets'))
if (ROOT_DIR / 'README_Windows.md').exists():
    datas.append((str(ROOT_DIR / 'README_Windows.md'), '.'))
if (ROOT_DIR / 'EULA.txt').exists():
    datas.append((str(ROOT_DIR / 'EULA.txt'), '.'))

# Windows-specific binaries
if sys.platform == 'win32':
    adb = ROOT_DIR / 'platform-tools' / 'adb.exe'
    fastboot = ROOT_DIR / 'platform-tools' / 'fastboot.exe'
    if adb.exists():
        binaries.append((str(adb), '.'))
    if fastboot.exists():
        binaries.append((str(fastboot), '.'))

hidden_imports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'usb.core',
    'usb.util',
    'serial',
    'serial.tools.list_ports',
    'modules.exploits.qualcomm_edl_exploit',
    'modules.exploits.mediatek_brom_exploit',
    'modules.exploits.samsung_frp_exploit',
    'modules.exploits.google_pixel_frp_exploit',
    'modules.exploits.huawei_frp_exploit',
    'modules.exploits.lockscreen_removal_exploit',
    'modules.exploits.imei_qcn_exploit',
]

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[str(ROOT_DIR)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='unlock_tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)