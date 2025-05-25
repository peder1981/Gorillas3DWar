#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar um pacote .app para macOS
"""
import os
import sys
import shutil
import subprocess
import plistlib
from pathlib import Path

def criar_estrutura_app():
    """Cria a estrutura básica do aplicativo macOS"""
    print("Criando estrutura de aplicativo macOS (.app)...")
    
    # Define os caminhos
    app_path = os.path.join("dist", "Gorillas3DWar.app")
    contents_path = os.path.join(app_path, "Contents")
    macos_path = os.path.join(contents_path, "MacOS")
    resources_path = os.path.join(contents_path, "Resources")
    frameworks_path = os.path.join(contents_path, "Frameworks")
    
    # Cria as pastas
    os.makedirs(app_path, exist_ok=True)
    os.makedirs(contents_path, exist_ok=True)
    os.makedirs(macos_path, exist_ok=True)
    os.makedirs(resources_path, exist_ok=True)
    os.makedirs(frameworks_path, exist_ok=True)
    
    return {
        "app_path": app_path,
        "contents_path": contents_path,
        "macos_path": macos_path,
        "resources_path": resources_path,
        "frameworks_path": frameworks_path
    }

def criar_info_plist(contents_path):
    """Cria o arquivo Info.plist"""
    print("Criando arquivo Info.plist...")
    
    info = {
        'CFBundleName': 'Gorillas3DWar',
        'CFBundleDisplayName': 'Gorillas 3D War',
        'CFBundleIdentifier': 'com.gorillas3dwar',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'CFBundleExecutable': 'gorillas3d',
        'CFBundleIconFile': 'AppIcon.icns',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.9.0',
        'NSPrincipalClass': 'NSApplication',
    }
    
    plist_path = os.path.join(contents_path, "Info.plist")
    with open(plist_path, 'wb') as f:
        plistlib.dump(info, f)

def criar_script_inicializacao(macos_path):
    """Cria o script de inicialização para o aplicativo"""
    print("Criando script de inicialização...")
    
    launcher_path = os.path.join(macos_path, "gorillas3d")
    with open(launcher_path, 'w') as f:
        f.write("""#!/bin/bash
# Script de inicialização para Gorillas 3D War no macOS

# Obtém o diretório do script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RESOURCES="$DIR/../Resources"

# Adiciona o diretório Resources ao PYTHONPATH
export PYTHONPATH="$RESOURCES:$PYTHONPATH"

# Executa o Python com o script principal
exec /usr/bin/env python3 "$RESOURCES/main.py"
""")
    
    # Torna o script executável
    os.chmod(launcher_path, 0o755)

def copiar_recursos(paths):
    """Copia os recursos do jogo para o pacote .app"""
    print("Copiando recursos do jogo...")
    
    # Copia os arquivos da pasta dist/Gorillas3DWar para Resources
    dist_path = os.path.join("dist", "Gorillas3DWar")
    if os.path.exists(dist_path):
        for item in os.listdir(dist_path):
            src = os.path.join(dist_path, item)
            dst = os.path.join(paths["resources_path"], item)
            
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
    
    # Cria ícone padrão se não existir
    icns_path = os.path.join(paths["resources_path"], "AppIcon.icns")
    if not os.path.exists(icns_path):
        # Se não tiver um ícone .icns, cria um arquivo vazio
        with open(icns_path, 'wb') as f:
            f.write(b'')

def criar_dmg():
    """Cria um arquivo .dmg para distribuição"""
    print("Criando arquivo DMG para distribuição...")
    
    try:
        app_path = os.path.join("dist", "Gorillas3DWar.app")
        dmg_path = "Gorillas3DWar.dmg"
        
        # Verifica se o comando hdiutil está disponível (apenas em macOS)
        result = subprocess.run(["which", "hdiutil"], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Estamos em um macOS, podemos criar o DMG
            cmd = [
                "hdiutil", "create", 
                "-volname", "Gorillas 3D War", 
                "-srcfolder", app_path, 
                "-ov", "-format", "UDZO", 
                dmg_path
            ]
            subprocess.run(cmd, check=True)
            print(f"Arquivo DMG criado: {dmg_path}")
        else:
            # Não estamos em um macOS, apenas compactamos a pasta .app
            print("Comando hdiutil não encontrado (normal em sistemas não-macOS).")
            print("Criando um arquivo ZIP em vez de DMG...")
            
            import zipfile
            with zipfile.ZipFile("Gorillas3DWar_macOS.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(app_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(
                            file_path, 
                            os.path.relpath(file_path, os.path.dirname(app_path))
                        )
            
            print("Arquivo ZIP criado: Gorillas3DWar_macOS.zip")
    except Exception as e:
        print(f"Erro ao criar arquivo de distribuição: {e}")
        print("Você pode distribuir a pasta .app diretamente.")

def main():
    """Função principal"""
    print("=== Criação de Pacote macOS para Gorillas 3D War ===")
    
    # Cria a estrutura do aplicativo
    paths = criar_estrutura_app()
    
    # Cria o arquivo Info.plist
    criar_info_plist(paths["contents_path"])
    
    # Cria o script de inicialização
    criar_script_inicializacao(paths["macos_path"])
    
    # Copia os recursos
    copiar_recursos(paths)
    
    # Cria arquivo DMG para distribuição
    criar_dmg()
    
    print("\nPacote macOS criado com sucesso!")
    print(f"O aplicativo está disponível em: {paths['app_path']}")
    print("\nInstruções para distribuição:")
    print("1. No macOS, distribua o arquivo .dmg ou .zip")
    print("2. O usuário precisará ter Python 3.7+ e Panda3D instalados")
    print("3. Pode ser necessário ajustar as permissões de segurança no macOS")

if __name__ == "__main__":
    main()
