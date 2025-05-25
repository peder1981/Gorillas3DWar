#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script unificado para distribuição do Gorillas 3D War em múltiplas plataformas
"""
import os
import sys
import platform
import subprocess
import shutil
import argparse
from pathlib import Path

def verificar_requisitos():
    """Verifica se os requisitos básicos estão presentes"""
    print("Verificando requisitos de empacotamento...")
    
    # Verifica se o Python está instalado (óbvio, já que estamos executando Python)
    print("✓ Python disponível")
    
    # Verifica se o Panda3D está instalado
    try:
        import panda3d
        print(f"✓ Panda3D disponível (versão: {getattr(panda3d, '__version__', 'desconhecida')})")
    except ImportError:
        print("✗ Panda3D não encontrado. Considere instalar: pip install panda3d")
    
    # Verifica plataforma atual
    sistema = platform.system().lower()
    print(f"✓ Sistema operacional detectado: {sistema}")
    
    return sistema

def empacotar_basico():
    """Cria um pacote básico do jogo (funciona em todas as plataformas)"""
    print("\n=== Criando pacote básico do jogo ===")
    
    # Executa o script distribuir.py para criar o pacote básico
    if os.path.exists("distribuir.py"):
        subprocess.run([sys.executable, "distribuir.py"])
    else:
        print("Erro: arquivo distribuir.py não encontrado")

def empacotar_windows():
    """Cria um instalador para Windows usando NSIS"""
    print("\n=== Criando instalador para Windows ===")
    
    # Verifica se o NSIS está instalado
    nsis_found = False
    
    if platform.system().lower() == "windows":
        # Procura o NSIS no Windows
        makensis_paths = [
            r"C:\Program Files\NSIS\makensis.exe",
            r"C:\Program Files (x86)\NSIS\makensis.exe"
        ]
        for path in makensis_paths:
            if os.path.exists(path):
                nsis_found = True
                nsis_cmd = [path, "instalador_windows.nsi"]
                break
    else:
        # Em sistemas Unix, procura o comando 'makensis'
        try:
            subprocess.run(["which", "makensis"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            nsis_found = True
            nsis_cmd = ["makensis", "instalador_windows.nsi"]
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
    
    if nsis_found:
        try:
            # Gera o pacote básico primeiro
            empacotar_basico()
            
            # Executa o NSIS para criar o instalador
            print("Criando instalador Windows com NSIS...")
            subprocess.run(nsis_cmd, check=True)
            print("Instalador Windows criado com sucesso!")
        except subprocess.SubprocessError as e:
            print(f"Erro ao criar instalador Windows: {e}")
    else:
        print("NSIS (makensis) não encontrado. O instalador Windows não pode ser criado.")
        print("Para instalar NSIS:")
        print("  - Windows: https://nsis.sourceforge.io/Download")
        print("  - Linux: sudo apt-get install nsis (Ubuntu/Debian)")
        print("  - macOS: brew install nsis (com Homebrew)")

def empacotar_macos():
    """Cria um pacote .app para macOS"""
    print("\n=== Criando pacote para macOS ===")
    
    if os.path.exists("macos_bundler.py"):
        # Gera o pacote básico primeiro
        empacotar_basico()
        
        # Executa o script para criar o pacote macOS
        subprocess.run([sys.executable, "macos_bundler.py"])
    else:
        print("Erro: arquivo macos_bundler.py não encontrado")

def empacotar_linux():
    """Cria um AppImage para Linux"""
    print("\n=== Criando AppImage para Linux ===")
    
    if os.path.exists("criar_appimage.sh"):
        # Gera o pacote básico primeiro
        empacotar_basico()
        
        # Torna o script executável
        try:
            os.chmod("criar_appimage.sh", 0o755)
        except:
            pass
        
        # Executa o script para criar o AppImage
        try:
            subprocess.run(["./criar_appimage.sh"], check=True)
        except subprocess.SubprocessError as e:
            print(f"Erro ao criar AppImage: {e}")
    else:
        print("Erro: arquivo criar_appimage.sh não encontrado")

def criar_pacote_completo():
    """Cria pacotes para todas as plataformas suportadas"""
    print("\n=== Criando pacotes para todas as plataformas ===")
    
    # Cria o pacote básico primeiro
    empacotar_basico()
    
    # Detecta o sistema atual
    sistema = platform.system().lower()
    
    # Cria o pacote específico para o sistema atual
    if sistema == "windows":
        empacotar_windows()
    elif sistema == "darwin":
        empacotar_macos()
    elif sistema == "linux":
        empacotar_linux()
    
    print("\nTodos os pacotes foram criados com sucesso!")

def criar_pacote_especifico(tipo_pacote):
    """Cria um pacote específico baseado na escolha do usuário"""
    if tipo_pacote == "windows":
        empacotar_windows()
    elif tipo_pacote == "macos":
        empacotar_macos()
    elif tipo_pacote == "linux":
        empacotar_linux()
    elif tipo_pacote == "basico":
        empacotar_basico()
    else:
        print(f"Tipo de pacote desconhecido: {tipo_pacote}")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Ferramenta de empacotamento para Gorillas 3D War")
    
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--windows", action="store_true", help="Criar pacote para Windows")
    grupo.add_argument("--macos", action="store_true", help="Criar pacote para macOS")
    grupo.add_argument("--linux", action="store_true", help="Criar pacote para Linux (AppImage)")
    grupo.add_argument("--basico", action="store_true", help="Criar pacote básico (multiplataforma)")
    grupo.add_argument("--todos", action="store_true", help="Criar pacotes para todas as plataformas")
    
    args = parser.parse_args()
    
    print("=== Ferramenta de Empacotamento do Gorillas 3D War ===")
    sistema = verificar_requisitos()
    
    if args.windows:
        criar_pacote_especifico("windows")
    elif args.macos:
        criar_pacote_especifico("macos")
    elif args.linux:
        criar_pacote_especifico("linux")
    elif args.basico:
        criar_pacote_especifico("basico")
    elif args.todos:
        criar_pacote_completo()
    else:
        # Nenhuma opção especificada, pergunte ao usuário
        print("\nEscolha o tipo de pacote a ser criado:")
        print("1. Pacote básico (multiplataforma)")
        print("2. Instalador para Windows")
        print("3. Pacote para macOS (.app)")
        print("4. AppImage para Linux")
        print("5. Todos os acima")
        
        escolha = input("\nDigite o número da opção desejada (1-5): ")
        
        if escolha == "1":
            criar_pacote_especifico("basico")
        elif escolha == "2":
            criar_pacote_especifico("windows")
        elif escolha == "3":
            criar_pacote_especifico("macos")
        elif escolha == "4":
            criar_pacote_especifico("linux")
        elif escolha == "5":
            criar_pacote_completo()
        else:
            print("Opção inválida. Criando pacote básico por padrão.")
            criar_pacote_especifico("basico")

if __name__ == "__main__":
    main()
