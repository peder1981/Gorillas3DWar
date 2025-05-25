# -*- mode: python ; coding: utf-8 -*-

import platform
import os
import sys

block_cipher = None

# Determina o sistema operacional atual
if platform.system() == 'Windows':
    sistema = 'windows'
elif platform.system() == 'Darwin':
    sistema = 'macos'
else:
    sistema = 'linux'

# Arquivos e pastas para incluir no executável
added_files = [
    ('models/', 'models/'),
    ('textures/', 'textures/'),
    ('sounds/', 'sounds/'),
    ('src/', 'src/'),
    ('assets/', 'assets/'),
]

# Verifica e adiciona arquivos específicos de plataforma
if os.path.exists('platform_specific'):
    if sistema == 'windows' and os.path.exists('platform_specific/windows'):
        added_files.append(('platform_specific/windows/', 'platform_specific/windows/'))
    elif sistema == 'macos' and os.path.exists('platform_specific/macos'):
        added_files.append(('platform_specific/macos/', 'platform_specific/macos/'))
    elif sistema == 'linux' and os.path.exists('platform_specific/linux'):
        added_files.append(('platform_specific/linux/', 'platform_specific/linux/'))

# Importa os hooks personalizados para o Panda3D
sys.path.insert(0, os.path.dirname(os.path.abspath('panda3d_hooks.py')))
import panda3d_hooks

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files + panda3d_hooks.datas,
    hiddenimports=[
        'panda3d.core', 
        'panda3d.bullet',
        'panda3d.physics',
        'panda3d.direct',
        'direct.showbase',
        'direct.particles',
        'numpy',
        'PIL',
        'PIL._tkinter_finder',
    ] + panda3d_hooks.hiddenimports,
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
    [],
    exclude_binaries=True,
    name='Gorillas3DWar',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='texturas/icon.ico',  # Substitua pelo caminho do seu ícone
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Gorillas3DWar',
)

# Configuração específica para macOS
app = BUNDLE(
    coll,
    name='Gorillas3DWar.app',
    icon='texturas/icon.icns',  # Ícone para macOS
    bundle_identifier='com.gorillas3dwar',
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': 'True',
        'LSBackgroundOnly': 'False'
    },
)
