#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir definitivamente o arquivo effects.py
"""
import os

def corrigir_arquivo():
    # Fazer backup do arquivo original
    os.system("cp /home/peder/Gorillas3DWar/src/effects.py /home/peder/Gorillas3DWar/src/effects.py.original")
    
    # Ler o arquivo até a linha problemática
    with open("/home/peder/Gorillas3DWar/src/effects.py", "r") as f:
        linhas = f.readlines()
    
    # Localizar o início da função criar_explosao e da próxima função
    inicio_criar_explosao = None
    inicio_proxima_funcao = None
    
    for i, linha in enumerate(linhas):
        if "def criar_explosao(self" in linha:
            inicio_criar_explosao = i
        if "def _criar_centelhas_explosao" in linha and inicio_criar_explosao is not None:
            inicio_proxima_funcao = i
            break
    
    if inicio_criar_explosao is None or inicio_proxima_funcao is None:
        print("Não foi possível localizar as funções. Abortando.")
        return
    
    # Verificar se há um 'return' incorreto entre as funções
    return_problematico = None
    for i in range(inicio_criar_explosao + 1, inicio_proxima_funcao):
        if "return explosao" in linhas[i] and not linhas[i].startswith("        "):
            return_problematico = i
            break
    
    if return_problematico is not None:
        print(f"Encontrado return problemático na linha {return_problematico + 1}")
        # Corrigir a indentação do return
        linhas[return_problematico] = "        return explosao\n"
    
    # Garantir que a próxima função comece sem indentação extra
    if "    def _criar_centelhas_explosao" in linhas[inicio_proxima_funcao]:
        linhas[inicio_proxima_funcao] = linhas[inicio_proxima_funcao].replace("    def ", "    def ")
    
    # Escrever o arquivo corrigido
    with open("/home/peder/Gorillas3DWar/src/effects.py", "w") as f:
        f.writelines(linhas)
    
    print("Arquivo corrigido com sucesso!")

# Abordagem alternativa - reescrever a função completamente
def reescrever_funcao_criar_explosao():
    """Reescreve a função criar_explosao do zero para evitar problemas de sintaxe"""
    
    nova_funcao = """    def criar_explosao(self, posicao, raio=2.0, num_particulas=50, tipo='padrao'):
        \"\"\"
        Cria uma explosão na posição especificada com vários efeitos visuais.
        
        Args:
            posicao: Posição da explosão.
            raio: Raio da explosão.
            num_particulas: Número de partículas a serem criadas.
            tipo: Tipo de explosão ('padrao', 'grande', 'pequena', 'fogo').
        
        Returns:
            Dicionário com informações da explosão.
        \"\"\"
        # Ajusta parâmetros baseados no tipo de explosão
        if tipo == 'grande':
            raio *= 2.0
            num_particulas *= 2
            duracao = 3.0
            cor_base = (1.0, 0.6, 0.0)  # Laranja mais intenso
            num_fragmentos = 20
            forca_fisica = 1000.0
        elif tipo == 'pequena':
            raio *= 0.6
            num_particulas = max(10, num_particulas // 2)
            duracao = 1.0
            cor_base = (1.0, 0.8, 0.2)  # Amarelo
            num_fragmentos = 0
            forca_fisica = 200.0
        elif tipo == 'fogo':
            raio *= 1.2
            duracao = 4.0
            cor_base = (0.9, 0.3, 0.1)  # Vermelho mais intenso
            num_fragmentos = 5
            forca_fisica = 500.0
        else:  # padrao
            duracao = 2.0
            cor_base = (1.0, 0.5, 0.0)  # Laranja padrão
            num_fragmentos = 10
            forca_fisica = 500.0
        
        # Cria nó para a explosão na hierarquia correta
        explosao_node = NodePath(f"explosao_{len(self.explosoes)}")
        explosao_node.reparentTo(self.explosoes_node)
        explosao_node.setPos(posicao)
        
        # Inicializa o dicionário da explosão
        explosao = {
            'node': explosao_node,
            'posicao': LPoint3(*posicao),
            'raio': raio,
            'tempo_vida': duracao,
            'tempo_inicial': duracao,
            'tipo': tipo
        }
        
        # Adiciona luzes para a explosão
        luzes = self._criar_luzes_explosao(explosao_node, cor_base, raio)
        explosao['luzes'] = luzes
        
        # Cria a onda de choque (esfera que expande)
        onda_choque = self._criar_onda_choque(explosao_node, cor_base, raio)
        explosao['onda_choque'] = onda_choque
        
        # Cria o flash de luz inicial
        flash = self._criar_flash_explosao(explosao_node, cor_base, raio)
        explosao['flash'] = flash
        
        # Cria as partículas de explosão
        particulas = self._criar_particulas_explosao(explosao_node, num_particulas, raio, cor_base, duracao)
        explosao['particulas'] = particulas
        
        # Cria centelhas
        num_centelhas = max(5, int(num_particulas * 0.3))
        centelhas = self._criar_centelhas_explosao(explosao_node, num_centelhas, raio)
        explosao['centelhas'] = centelhas
        
        # Cria fumaça
        num_nuvens_fumaca = max(3, int(num_particulas * 0.2))
        self._criar_fumaca_explosao(explosao, num_nuvens_fumaca, raio, duracao)
        
        # Aplica efeitos de física se o sistema estiver disponível
        if self.sistema_fisica and self.usar_fisica_avancada:
            # Aplica força de explosão a objetos próximos
            self.sistema_fisica.aplicar_forca_explosao(
                posicao, raio * 2.0, forca_fisica, afetar_predios=(tipo == 'grande')
            )
            
            # Cria fragmentos se for uma explosão grande
            if num_fragmentos > 0:
                # Define o modelo para os fragmentos
                modelo_fragmento = "models/misc/box"
                
                # Cria fragmentos físicos
                fragmentos = self.sistema_fisica.criar_fragmentos_explosao(
                    posicao, modelo_fragmento, num_fragmentos, forca_fisica,
                    escala_fragmentos=0.2 * raio, tempo_vida=duracao
                )
                
                explosao['fragmentos_fisica'] = fragmentos
        
        # Adiciona à lista de explosões para ser gerenciada
        self.explosoes.append(explosao)
        
        # Atualiza estatísticas
        self.estatisticas['num_explosoes'] += 1
        self.estatisticas['num_particulas'] += len(particulas)
        if 'centelhas' in explosao:
            self.estatisticas['num_particulas'] += len(explosao['centelhas'])
        
        return explosao
"""
    
    # Ler o arquivo
    with open("/home/peder/Gorillas3DWar/src/effects.py", "r") as f:
        conteudo = f.read()
    
    # Encontrar a função criar_explosao atual
    inicio = conteudo.find("    def criar_explosao(self")
    if inicio == -1:
        print("Função criar_explosao não encontrada")
        return False
    
    # Encontrar a próxima função
    proxima_funcao = conteudo.find("    def _criar_centelhas_explosao", inicio)
    if proxima_funcao == -1:
        print("Função _criar_centelhas_explosao não encontrada")
        return False
    
    # Substituir a função atual pela nova
    novo_conteudo = conteudo[:inicio] + nova_funcao + conteudo[proxima_funcao:]
    
    # Escrever o novo conteúdo
    with open("/home/peder/Gorillas3DWar/src/effects.py", "w") as f:
        f.write(novo_conteudo)
    
    print("Função criar_explosao reescrita com sucesso!")
    return True

if __name__ == "__main__":
    print("Tentando corrigir o arquivo effects.py...")
    # Primeiro tenta corrigir o arquivo
    corrigir_arquivo()
    
    # Se não resolver, reescreve a função completamente
    reescrever_funcao_criar_explosao()
    
    print("Processo concluído.")
