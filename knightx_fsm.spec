# KnightX_fsm - PyInstaller Spec File
# Used for building standalone executables and AppImage

import sys
import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('config.py', '.'),
        ('encryption.py', '.'),
        ('database.py', '.'),
        ('ai_integration.py', '.'),
        ('file_operations.py', '.'),
        ('views', 'views'),
    ],
    hiddenimports=[
        'customtkinter',
        'psutil',
        'Crypto',
        'cryptography',
        'bcrypt',
        'jwt',
        'requests',
        'pyClamd',
    ],
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
    name='KnightX_fsm',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disabled_windowed=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='KnightX_fsm.app',
    icon=None,
    bundle_identifier=None,
    info_plist={
        'NSHighResolutionCapable': 'True',
    },
)