#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gorillas 3D War - Módulo para controle de câmera
"""
from panda3d.core import LPoint3, LVector3
import math

class GameCamera:
    """
    Classe para gerenciar a câmera do jogo, com diferentes modos de visualização.
    """
    def __init__(self, game):
        """
        Inicializa o controle de câmera.
        
        Args:
            game: Referência ao jogo principal.
        """
        self.game = game
        
        # Modo da câmera: 'gorila', 'panoramica', 'seguir_projetil', 'livre'
        self.modo = 'gorila'
        
        # Alvo atual da câmera
        self.alvo = None
        self.alvo_offset = LPoint3(0, 0, 0)
        
        # Distância da câmera no modo gorila
        self.distancia_camera = 10.0
        
        # Ângulos da câmera
        self.camera_h = 180  # ângulo horizontal (em torno do eixo Z)
        self.camera_p = -20  # ângulo vertical (elevação)
        
        # Configuração inicial
        self.configurar_camera_inicial()
        
    def configurar_camera_inicial(self):
        """
        Configura a posição inicial da câmera.
        """
        # Posiciona a câmera para uma visão geral da cidade
        self.game.camera.setPos(0, -50, 30)
        self.game.camera.lookAt(0, 0, 0)
        
    def atualizar(self, dt):
        """
        Atualiza a posição da câmera de acordo com o modo atual.
        
        Args:
            dt: Delta time (tempo desde o último frame).
        """
        if self.modo == 'gorila' and self.alvo:
            self.atualizar_camera_gorila(dt)
        elif self.modo == 'panoramica':
            self.atualizar_camera_panoramica(dt)
        elif self.modo == 'seguir_projetil':
            self.atualizar_camera_seguir_projetil(dt)
        # No modo 'livre', a câmera não é atualizada automaticamente
        
    def atualizar_camera_gorila(self, dt):
        """
        Atualiza a câmera no modo 'gorila', posicionando-a atrás do gorila ativo.
        
        Args:
            dt: Delta time (tempo desde o último frame).
        """
        if not self.alvo:
            return
            
        # Posição do alvo
        alvo_pos = self.alvo.get_pos()
        
        # Calcula a posição da câmera baseada nos ângulos e distância
        h_rad = math.radians(self.camera_h)
        p_rad = math.radians(self.camera_p)
        
        # Calcula o offset da câmera em coordenadas esféricas
        x_offset = -self.distancia_camera * math.sin(h_rad) * math.cos(p_rad)
        y_offset = -self.distancia_camera * math.cos(h_rad) * math.cos(p_rad)
        z_offset = -self.distancia_camera * math.sin(p_rad)
        
        # Posição da câmera
        camera_pos = alvo_pos + LPoint3(x_offset, y_offset, z_offset)
        
        # Suaviza a transição da câmera
        atual_pos = self.game.camera.getPos()
        nova_pos = atual_pos + (camera_pos - atual_pos) * min(1.0, dt * 5.0)
        
        # Atualiza a posição da câmera
        self.game.camera.setPos(nova_pos)
        
        # Faz a câmera olhar para o alvo
        self.game.camera.lookAt(alvo_pos + LPoint3(0, 0, 1))  # Olha um pouco acima do gorila
        
    def atualizar_camera_panoramica(self, dt):
        """
        Atualiza a câmera no modo 'panoramica', movendo-a lentamente para mostrar a cidade.
        
        Args:
            dt: Delta time (tempo desde o último frame).
        """
        # Ângulo atual
        tempo = self.game.taskMgr.globalClock.getFrameTime()
        angulo = tempo * 10  # Velocidade da rotação
        
        # Raio da circunferência
        raio = 50.0
        altura = 30.0
        
        # Calcula a nova posição da câmera
        x = raio * math.sin(math.radians(angulo))
        y = raio * math.cos(math.radians(angulo))
        
        # Atualiza a posição da câmera
        self.game.camera.setPos(x, y, altura)
        
        # Faz a câmera olhar para o centro da cidade
        self.game.camera.lookAt(0, 0, 0)
        
    def atualizar_camera_seguir_projetil(self, dt):
        """
        Atualiza a câmera no modo 'seguir_projetil', seguindo a banana ativa.
        
        Args:
            dt: Delta time (tempo desde o último frame).
        """
        if not self.alvo or not hasattr(self.alvo, 'get_pos'):
            return
            
        # Posição do projétil
        projetil_pos = self.alvo.get_pos()
        
        # Offset da câmera
        offset = LPoint3(-5, -5, 3)
        
        # Posição da câmera
        camera_pos = projetil_pos + offset
        
        # Suaviza a transição da câmera
        atual_pos = self.game.camera.getPos()
        nova_pos = atual_pos + (camera_pos - atual_pos) * min(1.0, dt * 10.0)
        
        # Atualiza a posição da câmera
        self.game.camera.setPos(nova_pos)
        
        # Faz a câmera olhar para o projétil
        self.game.camera.lookAt(projetil_pos)
        
    def focar_gorila(self, gorila):
        """
        Foca a câmera em um gorila específico.
        
        Args:
            gorila: O gorila a ser focado.
        """
        self.alvo = gorila
        self.modo = 'gorila'
        
        # Ajusta o ângulo da câmera com base na direção do gorila
        if gorila.nome == 'gorila1':
            self.camera_h = 180  # Olhando na direção do gorila 2
        else:
            self.camera_h = 0  # Olhando na direção do gorila 1
            
    def seguir_projetil(self, projetil):
        """
        Faz a câmera seguir um projétil.
        
        Args:
            projetil: O projétil a ser seguido.
        """
        self.alvo = projetil
        self.modo = 'seguir_projetil'
        
    def modo_panoramico(self):
        """
        Ativa o modo de câmera panorâmica.
        """
        self.modo = 'panoramica'
        self.alvo = None
        
    def modo_livre(self):
        """
        Ativa o modo de câmera livre, controlado pelo usuário.
        """
        self.modo = 'livre'
        self.alvo = None
        
    def alternar_modo_camera(self):
        """
        Alterna entre os diferentes modos de câmera.
        """
        if self.modo == 'gorila':
            self.modo_panoramico()
        elif self.modo == 'panoramica':
            self.modo_livre()
        else:
            # Se estiver no modo livre ou seguindo projétil, volta para o gorila
            if self.game.jogador_atual == 0:
                self.focar_gorila(self.game.gorila1)
            else:
                self.focar_gorila(self.game.gorila2)
