#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hooks personalizados para o PyInstaller incluir corretamente os módulos do Panda3D
"""
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Garante que todos os submódulos do Panda3D sejam incluídos
hiddenimports = collect_submodules('panda3d')

# Coleta todos os arquivos de dados do Panda3D (modelos, texturas, etc.)
datas = collect_data_files('panda3d')
