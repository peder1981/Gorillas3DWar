#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de distribuição para o Gorillas 3D War
"""
import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
import site
import zipfile

def obter_pasta_panda3d():
    """Localiza a pasta de instalação do Panda3D"""
    # Tenta diferentes abordagens para encontrar o Panda3D
    for path in site.getsitepackages():
        panda_path = os.path.join(path, "panda3d")
        if os.path.exists(panda_path):
            return panda_path
    
    # Se não encontrou nas pastas de site-packages, tenta pelo path do Python
    try:
        import panda3d
        return os.path.dirname(panda3d.__file__)
    except ImportError:
        print("ERRO: Panda3D não encontrado. Verifique se está instalado corretamente.")
        return None

def criar_diretorio_dist():
    """Cria o diretório de distribuição"""
    os.makedirs("dist", exist_ok=True)
    os.makedirs("build", exist_ok=True)

def limpar_diretorio_dist():
    """Limpa o diretório de distribuição"""
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    criar_diretorio_dist()

def copiar_arquivos_jogo():
    """Copia todos os arquivos do jogo para a pasta de distribuição"""
    destino = os.path.join("dist", "Gorillas3DWar")
    os.makedirs(destino, exist_ok=True)
    
    # Cria a pasta src no destino
    os.makedirs(os.path.join(destino, "src"), exist_ok=True)
    
    # Copia os arquivos Python do jogo
    if os.path.exists("src"):
        for arquivo in os.listdir("src"):
            if arquivo.endswith(".py"):
                shutil.copy2(os.path.join("src", arquivo), os.path.join(destino, "src", arquivo))
    
    # Copia arquivos principais
    if os.path.exists("main.py"):
        shutil.copy2("main.py", os.path.join(destino, "main.py"))
    
    # Copia pastas de recursos
    for pasta in ["models", "textures", "sounds", "assets"]:
        if os.path.exists(pasta):
            pasta_destino = os.path.join(destino, pasta)
            shutil.copytree(pasta, pasta_destino, dirs_exist_ok=True)
    
    return destino

def copiar_dependencias(destino):
    """Copia as dependências necessárias"""
    # Copia bibliotecas do Panda3D
    panda_path = obter_pasta_panda3d()
    if panda_path:
        panda_destino = os.path.join(destino, "panda3d")
        if not os.path.exists(panda_destino):
            os.makedirs(panda_destino, exist_ok=True)
        
        # Copia os arquivos .pyd/.so/.dll do Panda3D
        for arquivo in os.listdir(panda_path):
            if arquivo.endswith((".pyd", ".so", ".dll", ".dylib")):
                shutil.copy2(
                    os.path.join(panda_path, arquivo),
                    os.path.join(panda_destino, arquivo)
                )
        
        # Tenta copiar módulos adicionais
        try:
            modulos = ["core", "bullet", "physics", "direct"]
            for modulo in modulos:
                modulo_path = os.path.join(panda_path, modulo)
                if os.path.exists(modulo_path):
                    modulo_destino = os.path.join(panda_destino, modulo)
                    shutil.copytree(modulo_path, modulo_destino, dirs_exist_ok=True)
        except Exception as e:
            print(f"Aviso ao copiar módulos Panda3D: {e}")
    
    # Cria script de inicialização para cada plataforma
    criar_scripts_inicializacao(destino)

def criar_scripts_inicializacao(destino):
    """Cria scripts de inicialização para cada plataforma"""
    sistema = platform.system().lower()
    
    # Script Python para todas as plataformas
    with open(os.path.join(destino, "iniciar.py"), "w", encoding="utf-8") as f:
        f.write("""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

# Adiciona diretórios ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importa e executa o jogo
from main import main
main()
""")
    
    # Script específico para Windows
    if sistema == "windows" or True:  # Criar para todas as plataformas
        with open(os.path.join(destino, "iniciar.bat"), "w", encoding="utf-8") as f:
            f.write("""@echo off
python iniciar.py
pause
""")
    
    # Script específico para Linux/macOS
    if sistema == "linux" or sistema == "darwin" or True:  # Criar para todas as plataformas
        shell_script = os.path.join(destino, "iniciar.sh")
        with open(shell_script, "w", encoding="utf-8") as f:
            f.write("""#!/bin/bash
python3 iniciar.py
""")
        # Torna o script executável
        try:
            os.chmod(shell_script, 0o755)
        except:
            print("Aviso: Não foi possível tornar o script iniciar.sh executável")

def criar_pacote_zip():
    """Cria um arquivo ZIP com a distribuição"""
    sistema = platform.system().lower()
    nome_sistema = "windows" if sistema == "windows" else "macos" if sistema == "darwin" else "linux"
    
    nome_zip = f"Gorillas3DWar_{nome_sistema}.zip"
    pasta_dist = os.path.join("dist", "Gorillas3DWar")
    
    with zipfile.ZipFile(nome_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(pasta_dist):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(
                    file_path, 
                    os.path.relpath(file_path, os.path.join("dist"))
                )
    
    print(f"Pacote criado: {nome_zip}")
    return nome_zip

def criar_readme_distribuicao():
    """Cria um README específico para a distribuição"""
    readme = os.path.join("dist", "Gorillas3DWar", "README.txt")
    
    with open(readme, "w", encoding="utf-8") as f:
        f.write("""GORILLAS 3D WAR
==============

Obrigado por baixar o Gorillas 3D War!

REQUISITOS:
- Python 3.7 ou superior
- Panda3D 1.10.13 ou superior

INSTALAÇÃO:
1. Certifique-se de ter o Python instalado
   - Windows: https://www.python.org/downloads/
   - Linux: Use o gerenciador de pacotes da sua distribuição
   - macOS: https://www.python.org/downloads/ ou use o homebrew

2. Instale o Panda3D:
   pip install panda3d

3. Execute o jogo:
   - Windows: Clique duas vezes em iniciar.bat
   - Linux/macOS: Execute ./iniciar.sh

CONTROLES:
- W/S: Ajusta o ângulo de lançamento (cima/baixo)
- A/D: Ajusta o ângulo de lançamento (esquerda/direita)
- Q/E: Ajusta a força do lançamento
- Espaço: Lança a banana
- R: Reinicia o jogo
- C: Alterna câmeras
- F: Tela cheia
- ESC: Sai do jogo

Em caso de problemas, verifique:
1. Se o Python está instalado corretamente
2. Se o Panda3D está instalado corretamente
3. Se todos os arquivos foram extraídos corretamente

Divirta-se!
""")

def main():
    """Função principal"""
    print("=== Distribuição do Gorillas 3D War ===")
    
    # Limpa e cria diretórios
    limpar_diretorio_dist()
    
    # Copia os arquivos do jogo
    print("Copiando arquivos do jogo...")
    destino = copiar_arquivos_jogo()
    
    # Copia as dependências
    print("Copiando dependências...")
    copiar_dependencias(destino)
    
    # Cria README de distribuição
    criar_readme_distribuicao()
    
    # Cria pacote ZIP
    print("Criando pacote ZIP...")
    nome_zip = criar_pacote_zip()
    
    print(f"\nDistribuição concluída com sucesso!")
    print(f"O pacote '{nome_zip}' está pronto para distribuição.")
    print("\nPara instalar em outra máquina:")
    print("1. Extraia o arquivo ZIP")
    print("2. Certifique-se de que Python 3.7+ e Panda3D estão instalados")
    print("3. Execute o script de inicialização apropriado para sua plataforma")

if __name__ == "__main__":
    main()
