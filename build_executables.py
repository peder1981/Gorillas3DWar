#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para construir executáveis do Gorillas 3D War para diferentes plataformas
"""
import os
import platform
import subprocess
import shutil
from pathlib import Path

def criar_pastas():
    """Cria as pastas necessárias para os executáveis"""
    os.makedirs("dist", exist_ok=True)
    os.makedirs("build", exist_ok=True)
    os.makedirs("executaveis", exist_ok=True)

def limpar_builds_anteriores():
    """Remove builds anteriores para evitar conflitos"""
    print("Limpando builds anteriores...")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")

def construir_executavel(plataforma):
    """Constrói o executável para a plataforma especificada"""
    print(f"Construindo executável para {plataforma}...")
    
    # Quando usamos um arquivo .spec, não podemos passar opções adicionais
    # As configurações devem estar no arquivo .spec
    comando = ["pyinstaller", "gorillas3d.spec"]
    
    # Executa o comando
    try:
        subprocess.run(comando, check=True)
        print(f"Executável para {plataforma} construído com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao construir executável para {plataforma}: {e}")
        return False

def empacotar_executavel(plataforma):
    """Copia os executáveis para a pasta de distribuição"""
    print(f"Empacotando executável para {plataforma}...")
    
    # Define o nome do executável e extensão por plataforma
    nome_executavel = "Gorillas3DWar"
    if plataforma == "windows":
        nome_executavel += ".exe"
    
    # Define os caminhos de origem e destino
    origem = os.path.join("dist", nome_executavel)
    destino = os.path.join("executaveis", f"{nome_executavel}_{plataforma}")
    
    # Para macOS, o destino é um .app
    if plataforma == "macos":
        origem = os.path.join("dist", f"{nome_executavel}.app")
        destino = os.path.join("executaveis", f"{nome_executavel}_{plataforma}.app")
    
    # Copia o executável para a pasta de distribuição
    if os.path.exists(origem):
        if os.path.isdir(origem):
            shutil.copytree(origem, destino, dirs_exist_ok=True)
        else:
            shutil.copy2(origem, destino)
        print(f"Executável para {plataforma} empacotado com sucesso!")
        return True
    else:
        print(f"Erro: Executável para {plataforma} não encontrado em {origem}")
        return False

def main():
    """Função principal"""
    print("=== Construção de Executáveis do Gorillas 3D War ===")
    
    # Prepara o ambiente
    criar_pastas()
    limpar_builds_anteriores()
    
    # Detecta a plataforma atual
    sistema_atual = platform.system().lower()
    plataforma = None
    
    if "windows" in sistema_atual:
        plataforma = "windows"
    elif "darwin" in sistema_atual:
        plataforma = "macos"
    elif "linux" in sistema_atual:
        plataforma = "linux"
    else:
        print(f"Sistema operacional não reconhecido: {sistema_atual}")
        return
    
    print(f"Sistema operacional detectado: {plataforma}")
    
    # Constrói e empacota o executável para a plataforma atual
    if construir_executavel(plataforma):
        empacotar_executavel(plataforma)
        
        print("\nInstruções para distribuição:")
        print("1. Os executáveis estão na pasta 'executaveis'")
        print("2. Para Windows: Distribua o arquivo .exe juntamente com todas as DLLs e recursos")
        print("3. Para macOS: Distribua o arquivo .app como um aplicativo completo")
        print("4. Para Linux: Distribua o arquivo binário e verifique as dependências necessárias")
        
        print("\nPara compilar para outras plataformas, execute este script no sistema operacional desejado.")
    
    print("\nProcesso concluído!")

if __name__ == "__main__":
    main()
