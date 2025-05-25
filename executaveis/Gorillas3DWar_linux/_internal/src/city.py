#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gorillas 3D War - Módulo de geração da cidade
"""
from panda3d.core import NodePath, Texture, TextureStage
from panda3d.core import CardMaker, PandaNode, LPoint3, LVector3
from direct.showbase.ShowBase import ShowBase
import random
import numpy as np

class Building:
    """
    Classe que representa um prédio na cidade 3D.
    """
    def __init__(self, game, x, y, height, width=None, depth=None):
        # Referência ao jogo
        self.game = game
        
        # Posição e dimensões
        self.x = x
        self.y = y
        self.height = height
        self.width = width if width else random.uniform(3.0, 7.0)
        self.depth = depth if depth else random.uniform(3.0, 7.0)
        
        # Cores do prédio (variações de cinza)
        self.color = (
            random.uniform(0.3, 0.5),
            random.uniform(0.3, 0.5),
            random.uniform(0.3, 0.6)
        )
        
        # Nó principal do prédio
        self.node = NodePath("building")
        self.node.reparentTo(game.render)
        self.node.setPos(x, y, 0)
        
        # Cria a geometria do prédio
        self.create_building()
        
        # Armazena quais janelas estão acesas
        self.lit_windows = []
        
        # Adiciona janelas ao prédio
        self.add_windows()
        
    def create_building(self):
        """
        Cria a geometria do prédio.
        """
        # Base do prédio (parte inferior)
        cm = CardMaker('building-bottom')
        cm.setFrame(0, self.width, 0, self.depth)
        bottom = self.node.attachNewNode(cm.generate())
        bottom.setP(-90)  # Rotação para ficar no chão
        bottom.setColor(*self.color)
        
        # Faces do prédio
        # Frente
        cm = CardMaker('building-front')
        cm.setFrame(0, self.width, 0, self.height)
        front = self.node.attachNewNode(cm.generate())
        front.setPos(0, self.depth, 0)
        front.setH(180)
        front.setColor(*self.color)
        
        # Trás
        cm = CardMaker('building-back')
        cm.setFrame(0, self.width, 0, self.height)
        back = self.node.attachNewNode(cm.generate())
        back.setPos(self.width, 0, 0)
        back.setH(0)
        back.setColor(*self.color)
        
        # Esquerda
        cm = CardMaker('building-left')
        cm.setFrame(0, self.depth, 0, self.height)
        left = self.node.attachNewNode(cm.generate())
        left.setPos(0, 0, 0)
        left.setH(90)
        left.setColor(*self.color)
        
        # Direita
        cm = CardMaker('building-right')
        cm.setFrame(0, self.depth, 0, self.height)
        right = self.node.attachNewNode(cm.generate())
        right.setPos(self.width, self.depth, 0)
        right.setH(-90)
        right.setColor(*self.color)
        
        # Topo
        cm = CardMaker('building-top')
        cm.setFrame(0, self.width, 0, self.depth)
        top = self.node.attachNewNode(cm.generate())
        top.setPos(0, 0, self.height)
        top.setP(-90)
        top.setColor(self.color[0] * 0.8, self.color[1] * 0.8, self.color[2] * 0.8)
        
        # Aplica textura (se disponível)
        # self.apply_texture()
        
    def add_windows(self):
        """
        Adiciona janelas ao prédio.
        """
        # Número de janelas horizontal e vertical
        windows_h = max(2, int(self.width / 0.8))
        windows_v = max(3, int(self.height / 1.2))
        
        # Tamanho das janelas
        window_width = (self.width * 0.8) / windows_h
        window_height = (self.height * 0.8) / windows_v
        
        # Espaçamento
        h_spacing = (self.width - (window_width * windows_h)) / (windows_h + 1)
        v_spacing = (self.height - (window_height * windows_v)) / (windows_v + 1)
        
        # Probabilidade de janela acesa
        lit_prob = 0.4
        
        # Adiciona janelas em cada face do prédio
        sides = ['front', 'back', 'left', 'right']
        for side in sides:
            for i in range(windows_h):
                for j in range(windows_v):
                    # Determina se a janela está acesa
                    is_lit = random.random() < lit_prob
                    window_color = (0.9, 0.9, 0.6) if is_lit else (0.1, 0.1, 0.2)
                    
                    # Posição da janela
                    x_pos = h_spacing + i * (window_width + h_spacing)
                    z_pos = v_spacing + j * (window_height + v_spacing)
                    
                    # Cria a janela
                    cm = CardMaker(f'window-{side}-{i}-{j}')
                    
                    if side in ['front', 'back']:
                        cm.setFrame(x_pos, x_pos + window_width, z_pos, z_pos + window_height)
                        window = self.node.attachNewNode(cm.generate())
                        
                        if side == 'front':
                            window.setPos(0, self.depth + 0.01, 0)
                            window.setH(180)
                        else:  # back
                            window.setPos(self.width, -0.01, 0)
                            window.setH(0)
                    else:  # left or right
                        w_depth = (self.depth * 0.8) / windows_h
                        d_spacing = (self.depth - (w_depth * windows_h)) / (windows_h + 1)
                        x_pos = d_spacing + i * (w_depth + d_spacing)
                        
                        cm.setFrame(x_pos, x_pos + w_depth, z_pos, z_pos + window_height)
                        window = self.node.attachNewNode(cm.generate())
                        
                        if side == 'left':
                            window.setPos(0, 0, 0)
                            window.setH(90)
                        else:  # right
                            window.setPos(self.width, self.depth, 0)
                            window.setH(-90)
                    
                    window.setColor(*window_color)
                    
                    # Guarda referência se estiver acesa
                    if is_lit:
                        self.lit_windows.append((side, i, j, window))
                        
    def get_top_position(self):
        """
        Retorna uma posição aleatória no topo do prédio.
        """
        x_pos = random.uniform(0.2 * self.width, 0.8 * self.width)
        y_pos = random.uniform(0.2 * self.depth, 0.8 * self.depth)
        return LPoint3(self.x + x_pos, self.y + y_pos, self.height)
        
    def apply_texture(self):
        """
        Aplica texturas ao prédio (se disponíveis).
        """
        # Implementação para carregar e aplicar texturas
        # Seria necessário ter os arquivos de textura disponíveis
        pass


class CityGenerator:
    """
    Gerador de cidade para o jogo Gorillas 3D War.
    """
    def __init__(self, game):
        """
        Inicializa o gerador de cidade.
        
        Args:
            game: Referência ao jogo principal.
        """
        self.game = game
        self.buildings = []
        self.city_node = NodePath("city")
        self.city_node.reparentTo(game.render)
        
        # Tamanho da cidade
        self.city_size = 100
        
        # Cria o chão da cidade
        self.create_ground()
        
    def create_ground(self):
        """
        Cria o chão da cidade.
        """
        # Tamanho do chão (bem maior que a cidade para dar sensação de amplitude)
        ground_size = self.city_size * 3
        
        # Cria o chão
        cm = CardMaker('ground')
        cm.setFrame(-ground_size/2, ground_size/2, -ground_size/2, ground_size/2)
        ground = self.city_node.attachNewNode(cm.generate())
        ground.setP(-90)  # Rotaciona para ficar no plano horizontal
        ground.setZ(-0.1)  # Ligeiramente abaixo de z=0 para evitar z-fighting
        
        # Cor de asfalto
        ground.setColor(0.2, 0.2, 0.2)
        
    def gerar_cidade(self, rows, cols):
        """
        Gera uma cidade com edifícios em grade.
        
        Args:
            rows: Número de linhas de prédios.
            cols: Número de colunas de prédios.
            
        Returns:
            NodePath do nó raiz da cidade.
        """
        # Limpa quaisquer prédios existentes
        self.limpar_cidade()
        
        # Espaçamento entre prédios
        building_spacing = 12
        street_width = 6
        
        # Calcula o tamanho total da cidade
        total_width = cols * building_spacing + (cols - 1) * street_width
        total_depth = rows * building_spacing + (rows - 1) * street_width
        
        # Posição inicial (canto inferior esquerdo da cidade)
        start_x = -total_width / 2
        start_y = -total_depth / 2
        
        # Gera os prédios em grade
        for row in range(rows):
            for col in range(cols):
                # Calcula a posição do prédio
                x = start_x + col * (building_spacing + street_width)
                y = start_y + row * (building_spacing + street_width)
                
                # Altura aleatória para o prédio
                height = random.uniform(10, 30)
                
                # Cria o prédio
                building = Building(self.game, x, y, height)
                self.buildings.append(building)
                
        # Retorna o nó da cidade
        return self.city_node
        
    def limpar_cidade(self):
        """
        Remove todos os prédios da cidade.
        """
        for building in self.buildings:
            building.node.removeNode()
        self.buildings = []
        
    @property
    def predios(self):
        """
        Retorna a lista de prédios.
        """
        return self.buildings
