#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para preparar o repositório do Gorillas3DWar para o GitHub
"""
import os
import subprocess
import sys

def executar_comando(comando, diretorio=None):
    """Executa um comando de shell e retorna a saída"""
    try:
        resultado = subprocess.run(
            comando, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            cwd=diretorio
        )
        return resultado.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar comando: {comando}")
        print(f"Saída de erro: {e.stderr}")
        return None

def criar_gitignore():
    """Cria um arquivo .gitignore adequado para o projeto"""
    gitignore_conteudo = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Arquivos temporários
.DS_Store
.env
.venv
env/
venv/
ENV/
tmp/
tmp_dist/
*.tmp
*.bak
*.swp

# Arquivos de distribuição
*.AppImage
*.exe
*.dmg
*.zip
*.tar.gz

# Ambiente de desenvolvimento
.idea/
.vscode/
.pytest_cache/
.coverage
htmlcov/

# Logs
*.log
"""
    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore_conteudo)
    print("✅ Arquivo .gitignore criado")

def criar_github_workflows():
    """Cria um workflow básico para GitHub Actions"""
    os.makedirs(".github/workflows", exist_ok=True)
    
    workflow_conteudo = """name: Gorillas3DWar CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
        
    - name: Lint with flake8
      run: |
        pip install flake8
        # Executa flake8 sem parar em erros, apenas para informação
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        
    - name: Build AppImage
      run: |
        python distribuir_gorillas.py
"""
    
    with open(".github/workflows/main.yml", "w", encoding="utf-8") as f:
        f.write(workflow_conteudo)
    print("✅ GitHub Actions workflow criado")

def inicializar_git():
    """Inicializa o repositório Git se ainda não estiver inicializado"""
    if not os.path.exists(".git"):
        executar_comando("git init")
        print("✅ Repositório Git inicializado")
    else:
        print("ℹ️ Repositório Git já está inicializado")

def verificar_status_git():
    """Verifica o status do repositório Git"""
    status = executar_comando("git status --porcelain")
    if status:
        print(f"\nArquivos prontos para commit:\n{status}")
    else:
        print("\nNão há alterações para commit.")

def main():
    diretorio_base = os.path.dirname(os.path.abspath(__file__))
    os.chdir(diretorio_base)
    
    print("🚀 Preparando o repositório Gorillas3DWar para o GitHub...")
    
    # Cria o arquivo .gitignore
    criar_gitignore()
    
    # Cria os arquivos de GitHub Actions
    criar_github_workflows()
    
    # Inicializa o repositório Git
    inicializar_git()
    
    # Verifica o status do Git
    verificar_status_git()
    
    print("""
🔥 Tudo pronto! Agora siga estas etapas:

1. Adicione os arquivos ao Git:
   git add .

2. Faça o commit inicial:
   git commit -m "Commit inicial do Gorillas3DWar"

3. Crie um novo repositório no GitHub:
   - Acesse https://github.com/new
   - Nomeie o repositório como "Gorillas3DWar"
   - Deixe-o público
   - Não inicialize com README, .gitignore ou licença (já temos esses arquivos)
   - Clique em "Criar repositório"

4. Associe seu repositório local ao GitHub:
   git remote add origin https://github.com/SEU_USUARIO/Gorillas3DWar.git
   git branch -M main
   git push -u origin main

5. Para configurar o patrocínio (GitHub Sponsors):
   - Acesse https://github.com/sponsors/dashboard
   - Siga as instruções para configurar seu perfil de patrocínio
   - Depois de aprovado, você poderá receber patrocínios

Lembre-se de substituir "SEU_USUARIO" pelo seu nome de usuário no GitHub.
    """)

if __name__ == "__main__":
    main()
