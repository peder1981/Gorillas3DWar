#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hooks personalizados para o PyInstaller incluir corretamente os módulos do Panda3D
"""
import os
import sys
import site
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Garante que todos os submódulos do Panda3D sejam incluídos
hiddenimports = collect_submodules('panda3d')

# Adiciona módulos 'direct' que são essenciais para o Panda3D
hiddenimports += [
    'direct',
    'direct.showbase',
    'direct.showbase.ShowBase',
    'direct.gui',
    'direct.gui.OnscreenText',
    'direct.gui.DirectGui',
    'direct.particles',
    'direct.particles.ParticleEffect',
    'direct.directtools',
    'direct.filter',
    'direct.interval',
    'direct.actor',
    'direct.task',
    'direct.controls',
]

# Coleta todos os arquivos de dados do Panda3D (modelos, texturas, etc.)
datas = collect_data_files('panda3d')

# Localiza o diretório de instalação do Panda3D para incluir o módulo 'direct'
def encontrar_pasta_direct():
    """Encontra a pasta do módulo direct do Panda3D"""
    # Locais possíveis para o módulo direct
    possibilidades = []
    
    # Verifica os diretórios de site-packages
    for path in site.getsitepackages():
        direct_path = os.path.join(path, 'direct')
        if os.path.isdir(direct_path):
            possibilidades.append((direct_path, 'direct'))
    
    # Verifica o diretório de instalação do Panda3D
    try:
        import panda3d
        panda3d_path = os.path.dirname(os.path.dirname(panda3d.__file__))
        direct_path = os.path.join(panda3d_path, 'direct')
        if os.path.isdir(direct_path):
            possibilidades.append((direct_path, 'direct'))
    except ImportError:
        pass
    
    return possibilidades

# Adiciona a pasta 'direct' aos dados a serem incluídos
for direct_path, target in encontrar_pasta_direct():
    print(f"Incluindo módulo direct de: {direct_path}")
    datas.append((direct_path, target))
