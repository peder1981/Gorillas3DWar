#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gorillas 3D War - Módulo para projéteis
"""
from panda3d.core import NodePath, CollisionSphere, CollisionNode
from panda3d.core import LPoint3, LVector3, LineSegs, BitMask32, CollisionRay
from panda3d.core import TransparencyAttrib, TextureStage, ColorBlendAttrib
import math
import random

class Banana:
    """
    Classe que representa uma banana (projétil) no jogo.
    """
    def __init__(self, game, posicao, angulo_horizontal, angulo_vertical, forca):
        """
        Inicializa uma banana.
        
        Args:
            game: Referência ao jogo principal.
            posicao: Posição inicial da banana.
            angulo_horizontal: Ângulo horizontal de lançamento (em graus).
            angulo_vertical: Ângulo vertical de lançamento (em graus).
            forca: Força do lançamento.
        """
        self.game = game
        self.posicao_inicial = posicao
        
        # Cria o nó principal da banana
        self.node = NodePath("banana")
        self.node.reparentTo(game.render)
        self.node.setPos(posicao)
        
        # Cria o modelo da banana
        self.criar_modelo()
        
        # Configura a física
        self.configurar_fisica(angulo_horizontal, angulo_vertical, forca)
        
        # Configura colisões
        self.configurar_colisoes()
        
        # Trajetória para efeito visual
        self.trajetoria = []
        self.max_pontos_trajetoria = 50
        self.linha_trajetoria = None
        
        # Rotação da banana
        self.rotacao = 0
        self.velocidade_rotacao = random.uniform(5, 15)
        
        # Tempo de vida da banana (para evitar que fique para sempre no mundo)
        self.tempo_vida = 15.0  # segundos
        
    def criar_modelo(self):
        """
        Cria o modelo 3D da banana.
        Idealmente, carregaríamos um modelo de um arquivo,
        mas para simplicidade usaremos formas básicas.
        """
        # Cor da banana
        cor_banana = (1.0, 0.9, 0.0)  # Amarelo
        
        # Corpo principal (forma de banana usando várias esferas)
        self.corpo = NodePath("banana_corpo")
        self.corpo.reparentTo(self.node)
        
        # Criamos uma forma curva de banana usando várias esferas
        # Parte central da banana
        centro = self.game.loader.loadModel("models/misc/sphere")
        centro.reparentTo(self.corpo)
        centro.setScale(0.3, 0.5, 0.25)
        centro.setColor(*cor_banana)
        
        # Ponta da banana (mais fina)
        ponta1 = self.game.loader.loadModel("models/misc/sphere")
        ponta1.reparentTo(self.corpo)
        ponta1.setPos(0.4, 0, 0.1)
        ponta1.setScale(0.15, 0.25, 0.15)
        ponta1.setColor(*cor_banana)
        
        # Outra ponta da banana
        ponta2 = self.game.loader.loadModel("models/misc/sphere")
        ponta2.reparentTo(self.corpo)
        ponta2.setPos(-0.4, 0, 0.1)
        ponta2.setScale(0.15, 0.25, 0.15)
        ponta2.setColor(*cor_banana)
        
        # Rotação inicial para dar uma curvatura à banana
        self.corpo.setP(-20)
        
        # Adiciona um efeito de brilho/glow para ficar mais visível
        self.criar_efeito_brilho()
        
    def configurar_fisica(self, angulo_horizontal, angulo_vertical, forca):
        """
        Configura a física do projétil.
        
        Args:
            angulo_horizontal: Ângulo horizontal de lançamento (em graus).
            angulo_vertical: Ângulo vertical de lançamento (em graus).
            forca: Força do lançamento.
        """
        # Converte ângulos para radianos
        ang_h_rad = math.radians(angulo_horizontal)
        ang_v_rad = math.radians(angulo_vertical)
        
        # Calcula as componentes da velocidade
        velocidade_base = forca * 0.1  # Ajusta a escala da força
        
        # Componentes da velocidade
        vx = velocidade_base * math.cos(ang_v_rad) * math.cos(ang_h_rad)
        vy = velocidade_base * math.cos(ang_v_rad) * math.sin(ang_h_rad)
        vz = velocidade_base * math.sin(ang_v_rad)
        
        # Define a velocidade inicial
        self.velocidade = LVector3(vx, vy, vz)
        
        # Armazena a posição atual como um LPoint3
        self.posicao = LPoint3(self.posicao_inicial)
        
    def criar_efeito_brilho(self):
        """
        Adiciona um efeito de brilho à banana para destacá-la.
        """
        # Cria uma esfera maior e semitransparente para o efeito de brilho
        glow = self.game.loader.loadModel("models/misc/sphere")
        glow.reparentTo(self.corpo)
        glow.setScale(1.5)  # Maior que a banana
        glow.setTransparency(TransparencyAttrib.MAlpha)
        glow.setColor(1.0, 1.0, 0.5, 0.3)  # Amarelo semitransparente
        glow.setLightOff()  # Não afetado por luzes
        glow.setBin('transparent', 10)  # Camada de renderização apropriada
        
        # Guarda referência ao glow
        self.glow = glow
        
    def configurar_colisoes(self):
        """
        Configura as colisões do projétil.
        """
        # Cria um nó de colisão para a banana
        coll_node = CollisionNode("banana_coll")
        coll_node.addSolid(CollisionSphere(0, 0, 0, 0.5))  # Esfera de colisão
        
        # Define a mascara de bits para as colisões
        coll_node.setFromCollideMask(BitMask32.bit(1))  # Colide com objetos no canal 1
        coll_node.setIntoCollideMask(BitMask32.allOff())  # Não gera eventos de colisão
        
        # Anexa o nó de colisão ao nó da banana
        self.coll_node_path = self.node.attachNewNode(coll_node)
        
        # Adiciona ao sistema de colisão do jogo
        self.game.cTrav.addCollider(self.coll_node_path, self.game.collisionHandler)
        
        # Torna a colisão invisível em tempo de execução
        self.coll_node_path.hide()
        
    def atualizar(self, gravidade, vento):
        """
        Atualiza a posição e velocidade da banana.
        
        Args:
            gravidade: Vetor de gravidade.
            vento: Vetor de vento.
            
        Returns:
            String indicando o estado da banana:
            - 'ativo': A banana ainda está em movimento.
            - 'colisao': A banana colidiu com algo.
            - 'fora_limites': A banana saiu dos limites do mundo.
        """
        # Atualiza o tempo de vida
        self.tempo_vida -= self.game.taskMgr.globalClock.getDt()
        if self.tempo_vida <= 0:
            return 'fora_limites'
        
        # Atualiza a velocidade considerando gravidade e vento
        self.velocidade += gravidade * self.game.taskMgr.globalClock.getDt()
        self.velocidade += vento * self.game.taskMgr.globalClock.getDt() * 0.3  # Reduz o efeito do vento
        
        # Atualiza a posição
        self.posicao += self.velocidade * self.game.taskMgr.globalClock.getDt()
        
        # Atualiza o nó com a nova posição
        self.node.setPos(self.posicao)
        
        # Atualiza a rotação
        self.rotacao += self.velocidade_rotacao
        self.node.setH(self.rotacao)
        self.node.setP(self.rotacao * 0.5)
        self.node.setR(self.rotacao * 0.3)
        
        # Armazena o ponto na trajetória
        self.trajetoria.append(LPoint3(self.posicao))
        if len(self.trajetoria) > self.max_pontos_trajetoria:
            self.trajetoria.pop(0)
            
        # Atualiza a linha da trajetória
        self.atualizar_linha_trajetoria()
        
        # Cria partículas de rastro
        if hasattr(self.game, 'efeitos'):
            if random.random() < 0.3:  # Reduz a frequência para melhorar desempenho
                self.game.efeitos.criar_rastro_banana(self.posicao)
                
        # Pulsa o efeito de brilho
        if hasattr(self, 'glow'):
            # Faz o glow pulsar lentamente
            tempo = self.game.taskMgr.globalClock.getFrameTime()
            fator_escala = 1.0 + 0.2 * math.sin(tempo * 5.0)
            self.glow.setScale(1.5 * fator_escala)
        
        # Verifica colisões
        # Em uma implementação completa, verificaríamos colisões com a cidade
        # usando o sistema de colisão do Panda3D
        
        # Verifica se saiu dos limites do mundo
        limite = 200  # unidades
        if (abs(self.posicao.getX()) > limite or 
            abs(self.posicao.getY()) > limite or 
            self.posicao.getZ() < -10 or
            self.posicao.getZ() > limite):
            return 'fora_limites'
            
        # Verifica se está muito próximo do chão
        if self.posicao.getZ() < 0.5:
            return 'colisao'
            
        return 'ativo'
        
    def atualizar_linha_trajetoria(self):
        """
        Atualiza a linha visual que representa a trajetória da banana.
        """
        # Remove a linha antiga se existir
        if self.linha_trajetoria:
            self.linha_trajetoria.removeNode()
            
        # Se não há pontos suficientes, não desenha
        if len(self.trajetoria) < 2:
            return
            
        # Cria uma nova linha
        ls = LineSegs()
        ls.setColor(1.0, 1.0, 0.0, 0.5)  # Amarelo semi-transparente
        ls.setThickness(2.0)
        
        # Adiciona os pontos da trajetória
        ls.moveTo(self.trajetoria[0])
        for ponto in self.trajetoria[1:]:
            ls.drawTo(ponto)
            
        # Cria o node path da linha
        linha_node = ls.create()
        self.linha_trajetoria = self.game.render.attachNewNode(linha_node)
        
    def verificar_colisao_com(self, outro_node):
        """
        Verifica se a banana colidiu com outro nó.
        
        Args:
            outro_node: O outro nó para verificar colisão.
            
        Returns:
            True se houve colisão, False caso contrário.
        """
        # Em uma implementação real, usaríamos o sistema de colisão do Panda3D
        # Por simplicidade, verificamos a distância entre os centros
        
        # Obtém as posições
        pos_banana = self.node.getPos()
        pos_outro = outro_node.getPos()
        
        # Calcula a distância
        distancia = (pos_banana - pos_outro).length()
        
        # Define um raio de colisão
        raio_colisao = 1.5
        
        # Retorna True se a distância for menor que o raio de colisão
        return distancia < raio_colisao
    
    def verificar_colisao_com_predio(self, predio):
        """
        Verifica se a banana colidiu com um prédio.
        
        Args:
            predio: O prédio para verificar colisão.
            
        Returns:
            True se houve colisão, False caso contrário.
        """
        # Obtém os limites do prédio
        predio_pos = predio.node.getPos()
        predio_min = LPoint3(predio_pos.getX(), predio_pos.getY(), predio_pos.getZ())
        predio_max = LPoint3(
            predio_min.getX() + predio.width,
            predio_min.getY() + predio.depth,
            predio_min.getZ() + predio.height
        )
        
        # Obtém a posição da banana
        banana_pos = self.node.getPos()
        
        # Raio da banana (para colisão)
        raio = 0.5
        
        # Verifica se a esfera da banana intersecta o retangulo do prédio
        # Encontra o ponto mais próximo no retangulo
        closest_x = max(predio_min.getX(), min(banana_pos.getX(), predio_max.getX()))
        closest_y = max(predio_min.getY(), min(banana_pos.getY(), predio_max.getY()))
        closest_z = max(predio_min.getZ(), min(banana_pos.getZ(), predio_max.getZ()))
        
        # Calcula a distância ao quadrado
        distance_squared = (
            (banana_pos.getX() - closest_x) ** 2 +
            (banana_pos.getY() - closest_y) ** 2 +
            (banana_pos.getZ() - closest_z) ** 2
        )
        
        # Verifica se a distância é menor que o raio ao quadrado
        return distance_squared <= (raio ** 2)
        
    def get_pos(self):
        """
        Retorna a posição atual da banana.
        """
        return self.posicao
        
    def remover(self):
        """
        Remove a banana do mundo.
        """
        # Remove a linha da trajetória
        if self.linha_trajetoria:
            self.linha_trajetoria.removeNode()
        
        # Remove do sistema de colisão
        if hasattr(self, 'coll_node_path'):
            self.game.cTrav.removeCollider(self.coll_node_path)
            
        # Remove o nó principal
        self.node.removeNode()
