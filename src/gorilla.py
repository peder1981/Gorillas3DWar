#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gorillas 3D War - Módulo para os personagens gorilas
"""
from panda3d.core import NodePath, CollisionSphere, CollisionNode
from panda3d.core import LPoint3, LVector3, TextNode
from direct.actor.Actor import Actor
import random
import math

class Gorilla:
    """
    Classe que representa um gorila no jogo.
    """
    def __init__(self, game, nome, cor, predio):
        """
        Inicializa um gorila.
        
        Args:
            game: Referência ao jogo principal.
            nome: Nome do gorila (identificador).
            cor: Cor do gorila (tuple RGB).
            predio: Prédio onde o gorila será posicionado.
        """
        self.game = game
        self.nome = nome
        self.cor = cor
        self.predio = predio
        
        # Cria o modelo do gorila
        self.node = NodePath(f"gorila_{nome}")
        self.node.reparentTo(game.render)
        
        # Posiciona no topo do prédio
        self.posicao = predio.get_top_position()
        self.node.setPos(self.posicao)
        
        # Cria a geometria do gorila
        self.criar_modelo()
        
        # Configura a física e colisões
        self.configurar_colisoes()
        
        # Direção que o gorila está olhando
        self.direcao = 1  # 1 para direita, -1 para esquerda
        
        # Estado de animação
        self.estado = "idle"
        
        # Adiciona texto flutuante com o nome do jogador
        self.criar_texto_jogador()
        
    def criar_modelo(self):
        """
        Cria o modelo 3D do gorila usando formas básicas.
        Idealmente, usaríamos um modelo 3D carregado de um arquivo,
        mas para simplicidade vamos criar um modelo básico.
        """
        # Corpo principal (esfera achatada)
        self.corpo = self.criar_esfera("corpo", 0, 0, 0, 0.8, self.cor)
        self.corpo.reparentTo(self.node)
        self.corpo.setScale(1.0, 0.8, 1.2)
        
        # Cabeça (esfera)
        self.cabeca = self.criar_esfera("cabeca", 0, 0, 1.4, 0.6, self.cor)
        self.cabeca.reparentTo(self.node)
        
        # Braços (cilindros)
        # Braço esquerdo
        self.braco_esq = self.criar_esfera("braco_esq", -0.9, 0, 0.5, 0.4, self.cor)
        self.braco_esq.reparentTo(self.node)
        self.braco_esq.setScale(0.5, 0.5, 1.3)
        
        # Braço direito
        self.braco_dir = self.criar_esfera("braco_dir", 0.9, 0, 0.5, 0.4, self.cor)
        self.braco_dir.reparentTo(self.node)
        self.braco_dir.setScale(0.5, 0.5, 1.3)
        
        # Pernas (cilindros)
        # Perna esquerda
        self.perna_esq = self.criar_esfera("perna_esq", -0.5, 0, -0.9, 0.4, self.cor)
        self.perna_esq.reparentTo(self.node)
        self.perna_esq.setScale(0.5, 0.5, 1.3)
        
        # Perna direita
        self.perna_dir = self.criar_esfera("perna_dir", 0.5, 0, -0.9, 0.4, self.cor)
        self.perna_dir.reparentTo(self.node)
        self.perna_dir.setScale(0.5, 0.5, 1.3)
        
        # Olhos (esferas brancas com pupilas pretas)
        # Olho esquerdo
        self.olho_esq = self.criar_esfera("olho_esq", -0.25, 0.5, 1.5, 0.15, (1, 1, 1))
        self.olho_esq.reparentTo(self.node)
        
        # Pupila esquerda
        self.pupila_esq = self.criar_esfera("pupila_esq", -0.25, 0.6, 1.5, 0.07, (0, 0, 0))
        self.pupila_esq.reparentTo(self.node)
        
        # Olho direito
        self.olho_dir = self.criar_esfera("olho_dir", 0.25, 0.5, 1.5, 0.15, (1, 1, 1))
        self.olho_dir.reparentTo(self.node)
        
        # Pupila direita
        self.pupila_dir = self.criar_esfera("pupila_dir", 0.25, 0.6, 1.5, 0.07, (0, 0, 0))
        self.pupila_dir.reparentTo(self.node)
        
        # Nariz (esfera pequena)
        self.nariz = self.criar_esfera("nariz", 0, 0.7, 1.4, 0.2, (0.8, 0.4, 0.4))
        self.nariz.reparentTo(self.node)
        
        # Boca (semi-esfera achatada)
        self.boca = self.criar_esfera("boca", 0, 0.65, 1.2, 0.3, (0.7, 0.3, 0.3))
        self.boca.reparentTo(self.node)
        self.boca.setScale(1.0, 0.5, 0.5)
        
        # Redimensiona o gorila todo
        self.node.setScale(0.8, 0.8, 0.8)
        
    def criar_esfera(self, nome, x, y, z, raio, cor):
        """
        Cria uma esfera com o nome, posição, raio e cor especificados.
        """
        # Usa a função loadModel do Panda3D para criar uma esfera
        esfera = self.game.loader.loadModel("models/misc/sphere")
        esfera.setName(nome)
        esfera.setPos(x, y, z)
        esfera.setScale(raio)
        esfera.setColor(*cor)
        return esfera
        
    def configurar_colisoes(self):
        """
        Configura as colisões do gorila.
        """
        # Cria um nó de colisão para o gorila
        coll_node = CollisionNode(f"{self.nome}_coll")
        coll_node.addSolid(CollisionSphere(0, 0, 0, 1.5))  # Esfera de colisão
        
        # Anexa o nó de colisão ao nó do gorila
        self.coll_node_path = self.node.attachNewNode(coll_node)
        
        # Torna a colisão invisível em tempo de execução
        self.coll_node_path.hide()
        
    def olhar_para(self, ponto):
        """
        Faz o gorila olhar para um ponto específico.
        
        Args:
            ponto: Coordenadas do ponto para onde olhar.
        """
        # Calcula a direção
        direcao = ponto - self.node.getPos()
        
        # Ajusta apenas o ângulo horizontal (no plano xz)
        angulo = math.degrees(math.atan2(direcao.getX(), direcao.getY()))
        self.node.setH(angulo)
        
        # Atualiza a direção para uso nas animações
        self.direcao = 1 if angulo > 0 else -1
        
    def olhar_para_outro_gorila(self, outro_gorila):
        """
        Faz o gorila olhar para outro gorila.
        
        Args:
            outro_gorila: O outro gorila para olhar.
        """
        self.olhar_para(outro_gorila.node.getPos())
        
    def animar(self, tipo_animacao):
        """
        Inicia uma animação no gorila.
        
        Args:
            tipo_animacao: Tipo de animação ("idle", "lançar", "comemorar", "triste").
        """
        self.estado = tipo_animacao
        
        # Implementação das animações
        if tipo_animacao == "lançar":
            # Animação de lançamento
            # Em uma implementação real, carregaríamos animações de um arquivo
            pass
        elif tipo_animacao == "comemorar":
            # Animação de comemoração
            pass
        elif tipo_animacao == "triste":
            # Animação de derrota
            pass
        else:  # idle
            # Animação padrão
            pass
            
    def atualizar(self, dt):
        """
        Atualiza o estado do gorila a cada frame.
        
        Args:
            dt: Delta time (tempo desde o último frame).
        """
        # Atualiza as animações
        if self.estado == "idle":
            # Faz um movimento suave de respiração
            amplitude = 0.02
            freq = 1.0
            offset = math.sin(self.game.taskMgr.globalClock.getFrameTime() * freq) * amplitude
            self.corpo.setScale(1.0 + offset, 0.8, 1.2 - offset)
            
    def get_pos(self):
        """
        Retorna a posição do gorila.
        """
        return self.node.getPos()
        
    def get_posicao_lancamento(self):
        """
        Retorna a posição de onde a banana será lançada.
        """
        # Posição da mão do gorila
        if self.direcao > 0:
            # Mão direita
            return self.node.getPos() + LPoint3(0.9, 0.5, 0.5)
        else:
            # Mão esquerda
            return self.node.getPos() + LPoint3(-0.9, 0.5, 0.5)
            
    def criar_texto_jogador(self):
        """
        Cria texto flutuante acima do gorila com o nome do jogador.
        """
        # Cria um nó de texto
        text_node = TextNode(f"{self.nome}_text")
        
        # Define o texto como "Jogador 1" ou "Jogador 2"
        jogador_num = "1" if self.nome == "gorila1" else "2"
        text_node.setText(f"Jogador {jogador_num}")
        
        # Configura a aparência do texto
        # Adiciona o componente alpha (1.0) à cor do jogador
        cor_rgba = (self.cor[0], self.cor[1], self.cor[2], 1.0)
        text_node.setTextColor(*cor_rgba)
        text_node.setAlign(TextNode.ACenter)
        text_node.setShadow(0.05, 0.05)
        text_node.setShadowColor(0, 0, 0, 1)
        
        # Cria o NodePath para o texto
        self.texto_np = self.game.render.attachNewNode(text_node)
        
        # Posiciona o texto acima do gorila
        self.texto_np.setPos(self.node.getPos() + LPoint3(0, 0, 2.5))
        
        # Configura o texto para sempre olhar para a câmera
        self.texto_np.setBillboardPointEye()
        
        # Escala o texto
        self.texto_np.setScale(0.5)
        
    def atualizar_texto(self):
        """
        Atualiza a posição do texto flutuante.
        """
        self.texto_np.setPos(self.node.getPos() + LPoint3(0, 0, 2.5))
        
    def destacar(self, ativo=True):
        """
        Destaca visualmente o gorila ativo.
        
        Args:
            ativo: True se o gorila está ativo, False caso contrário.
        """
        if ativo:
            # Adiciona um brilho ou efeito de destaque
            # Aumenta ligeiramente a escala
            self.node.setScale(0.9, 0.9, 0.9)
            
            # Poderia adicionar um efeito de brilho ou aura
            # Isso requer shaders ou outros efeitos mais avançados
        else:
            # Remove o destaque
            self.node.setScale(0.8, 0.8, 0.8)
