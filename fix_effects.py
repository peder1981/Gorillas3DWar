#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir o arquivo effects.py
"""
import os
import re

def corrigir_arquivo_effects():
    """Corrige problemas de indentação e sintaxe no arquivo effects.py"""
    
    arquivo_original = "/home/peder/Gorillas3DWar/src/effects.py"
    arquivo_backup = "/home/peder/Gorillas3DWar/src/effects.py.bak"
    
    # Cria um backup do arquivo original
    print(f"Criando backup em {arquivo_backup}")
    os.system(f"cp {arquivo_original} {arquivo_backup}")
    
    # Lê o conteúdo do arquivo
    with open(arquivo_original, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    
    # Procura pelo bloco da função criar_explosao
    inicio_criar_explosao = None
    fim_criar_explosao = None
    inicio_proxima_funcao = None
    
    for i, linha in enumerate(linhas):
        if re.match(r'\s*def criar_explosao\(', linha):
            inicio_criar_explosao = i
        elif inicio_criar_explosao is not None and re.match(r'\s*def _criar_centelhas_explosao\(', linha):
            inicio_proxima_funcao = i
            fim_criar_explosao = i - 1
            break
    
    if inicio_criar_explosao is None or fim_criar_explosao is None:
        print("Não foi possível localizar a função criar_explosao")
        return False
    
    print(f"Encontrada função criar_explosao nas linhas {inicio_criar_explosao} até {fim_criar_explosao}")
    
    # Verifica e corrige a indentação da função
    # Vamos garantir que todas as linhas dentro da função tenham a indentação correta
    indentacao_base = re.match(r'^(\s*)', linhas[inicio_criar_explosao]).group(1)
    indentacao_corpo = indentacao_base + "    "  # Adiciona 4 espaços para o corpo da função
    
    # Garante que o 'return' tenha a indentação correta
    for i in range(inicio_criar_explosao, fim_criar_explosao + 1):
        linha = linhas[i]
        if 'return explosao' in linha:
            # Garante que a linha de return tenha a indentação correta
            linhas[i] = indentacao_corpo + "return explosao\n"
    
    # Garante que a próxima função tenha a indentação correta
    if inicio_proxima_funcao:
        linhas[inicio_proxima_funcao] = indentacao_base + "def _criar_centelhas_explosao(self, node_pai, num_centelhas, raio):\n"
    
    # Garante que não haja linhas em branco com indentação incorreta entre as funções
    for i in range(fim_criar_explosao + 1, inicio_proxima_funcao):
        if linhas[i].strip() == "":
            linhas[i] = "\n"
    
    # Escreve o arquivo corrigido
    with open(arquivo_original, 'w', encoding='utf-8') as f:
        f.writelines(linhas)
    
    print("Arquivo effects.py corrigido com sucesso!")
    return True

if __name__ == "__main__":
    corrigir_arquivo_effects()
