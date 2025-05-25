#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gorillas 3D War - Módulo para sistema de destruição de prédios
"""
from panda3d.core import NodePath, CollisionSphere, CollisionNode
from panda3d.core import LPoint3, Vec3, BitMask32
import random
import math

class DestructionSystem:
    """
    Sistema de destruição para prédios e outros objetos do jogo.
    Permite que partes dos prédios sejam danificadas ou destruídas 
    quando atingidas por projéteis.
    """
    def __init__(self, game):
        """
        Inicializa o sistema de destruição.
        
        Args:
            game: Referência ao jogo principal.
        """
        self.game = game
        
        # Nó principal para os fragmentos de destruição
        self.fragments_node = NodePath("destruction_fragments")
        self.fragments_node.reparentTo(game.render)
        
        # Lista de fragmentos ativos
        self.fragments = []
        
        # Contador para IDs únicos de fragmentos
        self.fragment_id_counter = 0
        
        # Configuração
        self.max_fragments = 100  # Limite de fragmentos para evitar sobrecarga
        self.fragment_lifetime = 10.0  # Tempo de vida dos fragmentos em segundos
        
    def criar_explosao_predio(self, posicao, raio=2.0, predio=None):
        """
        Cria uma explosão que danifica ou destrói parte de um prédio.
        
        Args:
            posicao: Posição da explosão.
            raio: Raio da explosão.
            predio: Referência ao prédio atingido (opcional).
        """
        # Cria fragmentos de destruição
        self.criar_fragmentos(posicao, raio)
        
        # Se temos referência ao prédio, danos específicos nele
        if predio:
            self.danificar_predio(predio, posicao, raio)
            
        # Toca som de impacto
        if hasattr(self.game, 'som'):
            self.game.som.tocar_som('impacto_predio', posicao)
            
    def danificar_predio(self, predio, posicao, raio):
        """
        Causa danos a um prédio específico.
        
        Args:
            predio: Referência ao prédio.
            posicao: Posição do impacto.
            raio: Raio da explosão/impacto.
        """
        # Identifica a face do prédio atingida
        # As faces são: 'frente', 'trás', 'esquerda', 'direita', 'topo'
        
        # Obtém a posição relativa do impacto em relação ao prédio
        predio_pos = predio.node.getPos()
        rel_pos = posicao - predio_pos
        
        # Determina a face mais próxima do impacto
        face = self._determinar_face_atingida(predio, rel_pos)
        
        # Cria o efeito de dano na face apropriada
        self._criar_dano_na_face(predio, face, rel_pos, raio)
        
        # Atualiza o estado de dano do prédio
        if hasattr(predio, 'dano'):
            predio.dano += 0.1 * raio
        else:
            predio.dano = 0.1 * raio
            
        # Se o dano for muito grande, pode derrubar o prédio completamente
        if hasattr(predio, 'dano') and predio.dano > 0.9:
            self._derrubar_predio(predio)
            
    def _determinar_face_atingida(self, predio, rel_pos):
        """
        Determina qual face do prédio foi atingida.
        
        Args:
            predio: Referência ao prédio.
            rel_pos: Posição relativa do impacto.
            
        Returns:
            String indicando a face: 'frente', 'trás', 'esquerda', 'direita', 'topo'.
        """
        # Extrai as coordenadas relativas
        x, y, z = rel_pos.getX(), rel_pos.getY(), rel_pos.getZ()
        
        # Determina as dimensões do prédio
        width = predio.width
        depth = predio.depth
        height = predio.height
        
        # Verifica se atingiu o topo
        if z >= height * 0.9:
            return 'topo'
            
        # Calcula distâncias para cada face
        dist_frente = abs(y - depth)
        dist_tras = abs(y)
        dist_esquerda = abs(x)
        dist_direita = abs(x - width)
        
        # Determina a menor distância
        min_dist = min(dist_frente, dist_tras, dist_esquerda, dist_direita)
        
        if min_dist == dist_frente:
            return 'frente'
        elif min_dist == dist_tras:
            return 'tras'
        elif min_dist == dist_esquerda:
            return 'esquerda'
        else:
            return 'direita'
            
    def _criar_dano_na_face(self, predio, face, rel_pos, raio):
        """
        Cria um efeito visual de dano na face especificada do prédio.
        
        Args:
            predio: Referência ao prédio.
            face: Face do prédio ('frente', 'trás', 'esquerda', 'direita', 'topo').
            rel_pos: Posição relativa do impacto.
            raio: Raio do dano.
        """
        # Obtém a referência ao nó da face
        face_node = None
        
        # Em uma implementação real, teríamos acesso direto ao nó da face
        # Como estamos trabalhando com uma simplificação, vamos criar uma nova textura
        # que simula o dano e aplicá-la sobre a face atual
        
        # Cria uma "cratera" no prédio
        # Para simplificar, vamos usar uma esfera preta para simular o buraco
        crater = self.game.loader.loadModel("models/misc/sphere")
        crater.reparentTo(predio.node)
        
        # Configura a posição com base na face
        if face == 'frente':
            crater.setPos(rel_pos.getX(), predio.depth + 0.05, rel_pos.getZ())
        elif face == 'tras':
            crater.setPos(rel_pos.getX(), -0.05, rel_pos.getZ())
        elif face == 'esquerda':
            crater.setPos(-0.05, rel_pos.getY(), rel_pos.getZ())
        elif face == 'direita':
            crater.setPos(predio.width + 0.05, rel_pos.getY(), rel_pos.getZ())
        elif face == 'topo':
            crater.setPos(rel_pos.getX(), rel_pos.getY(), predio.height + 0.05)
            
        # Configura a aparência da cratera
        crater.setScale(raio * 0.5)
        crater.setColor(0.1, 0.1, 0.1, 0.8)  # Preto semitransparente
        crater.setTwoSided(True)  # Visível de ambos os lados
        crater.setDepthWrite(False)  # Evita problemas de Z-fighting
        
        # Adiciona alguma textura ou detalhe à cratera para parecer mais realista
        # Em uma implementação completa, usaríamos texturas específicas para os danos
        
        # Guarda referência à cratera no prédio
        if not hasattr(predio, 'crateras'):
            predio.crateras = []
            
        predio.crateras.append(crater)
        
        # Limita o número de crateras por prédio
        if len(predio.crateras) > 20:
            # Remove a cratera mais antiga
            predio.crateras[0].removeNode()
            predio.crateras.pop(0)
            
    def _derrubar_predio(self, predio):
        """
        Derruba completamente um prédio muito danificado.
        
        Args:
            predio: Referência ao prédio.
        """
        # Em uma implementação completa, teríamos um sistema de física
        # para simular o desabamento do prédio
        
        # Por enquanto, vamos simplesmente criar muitos fragmentos
        # e remover o prédio original
        
        posicao = predio.node.getPos()
        
        # Cria uma grande quantidade de fragmentos
        self.criar_fragmentos(posicao + LPoint3(predio.width/2, predio.depth/2, predio.height/2), 
                             raio=max(predio.width, predio.depth, predio.height) * 0.5,
                             quantidade=100)
        
        # Emite som de desabamento
        if hasattr(self.game, 'som'):
            self.game.som.tocar_som('impacto_predio', posicao, volume=1.0)
            
        # Remove o prédio da lista de prédios do jogo
        if predio in self.game.gerador_cidade.predios:
            self.game.gerador_cidade.predios.remove(predio)
            
        # Remove o nó do prédio
        predio.node.removeNode()
        
    def criar_fragmentos(self, posicao, raio=2.0, quantidade=20):
        """
        Cria fragmentos que voam da posição especificada.
        
        Args:
            posicao: Posição central onde os fragmentos são criados.
            raio: Raio da área de criação dos fragmentos.
            quantidade: Quantidade de fragmentos a serem criados.
        """
        # Limita a quantidade total de fragmentos
        quantidade_real = min(quantidade, self.max_fragments - len(self.fragments))
        
        # Cria os fragmentos
        for _ in range(quantidade_real):
            # Gera uma posição aleatória dentro do raio
            pos_offset = LPoint3(
                random.uniform(-raio, raio),
                random.uniform(-raio, raio),
                random.uniform(-raio, raio)
            )
            
            pos = posicao + pos_offset
            
            # Cria um fragmento
            self.criar_fragmento(pos)
            
    def criar_fragmento(self, posicao):
        """
        Cria um único fragmento.
        
        Args:
            posicao: Posição onde o fragmento é criado.
        """
        # Gera um ID único para o fragmento
        fragment_id = self.fragment_id_counter
        self.fragment_id_counter += 1
        
        # Cria o modelo do fragmento (usando uma forma simples)
        fragment = self.game.loader.loadModel("models/misc/sphere")
        fragment.reparentTo(self.fragments_node)
        fragment.setPos(posicao)
        
        # Escala aleatória
        escala = random.uniform(0.1, 0.5)
        fragment.setScale(escala, escala * random.uniform(0.5, 1.5), escala * random.uniform(0.5, 1.5))
        
        # Cor de concreto/tijolo
        r = random.uniform(0.4, 0.6)
        g = random.uniform(0.3, 0.5)
        b = random.uniform(0.2, 0.4)
        fragment.setColor(r, g, b)
        
        # Velocidade e rotação aleatórias
        vel_x = random.uniform(-5.0, 5.0)
        vel_y = random.uniform(-5.0, 5.0)
        vel_z = random.uniform(2.0, 8.0)
        
        rot_x = random.uniform(-10.0, 10.0)
        rot_y = random.uniform(-10.0, 10.0)
        rot_z = random.uniform(-10.0, 10.0)
        
        # Armazena o fragmento e seus dados
        self.fragments.append({
            'id': fragment_id,
            'node': fragment,
            'velocity': Vec3(vel_x, vel_y, vel_z),
            'rotation': Vec3(rot_x, rot_y, rot_z),
            'lifetime': self.fragment_lifetime
        })
        
    def atualizar(self, dt):
        """
        Atualiza todos os fragmentos.
        
        Args:
            dt: Delta time (tempo desde o último frame).
        """
        # Lista de fragmentos a serem removidos
        to_remove = []
        
        # Atualiza cada fragmento
        for fragment in self.fragments:
            # Atualiza o tempo de vida
            fragment['lifetime'] -= dt
            
            # Se o tempo de vida acabou, marca para remoção
            if fragment['lifetime'] <= 0:
                to_remove.append(fragment)
                continue
                
            # Atualiza a posição com base na velocidade
            pos = fragment['node'].getPos()
            vel = fragment['velocity']
            
            # Aplica gravidade
            vel.setZ(vel.getZ() - 9.8 * dt)
            
            # Atualiza a posição
            new_pos = pos + vel * dt
            fragment['node'].setPos(new_pos)
            
            # Atualiza a rotação
            h, p, r = fragment['node'].getHpr()
            rot = fragment['rotation']
            fragment['node'].setHpr(h + rot.getX() * dt, 
                                    p + rot.getY() * dt, 
                                    r + rot.getZ() * dt)
                                    
            # Verifica se o fragmento caiu no chão
            if new_pos.getZ() < 0:
                # Rebate com perda de energia
                fragment['velocity'].setZ(-vel.getZ() * 0.4)
                
                # Reduz velocidade horizontal (atrito)
                fragment['velocity'].setX(vel.getX() * 0.8)
                fragment['velocity'].setY(vel.getY() * 0.8)
                
                # Corrige a posição (acima do chão)
                fragment['node'].setZ(0.0)
                
                # Reduz o tempo de vida mais rapidamente após tocar o chão
                fragment['lifetime'] -= dt * 2.0
                
        # Remove os fragmentos marcados
        for fragment in to_remove:
            fragment['node'].removeNode()
            self.fragments.remove(fragment)
            
    def limpar(self):
        """
        Limpa todos os fragmentos.
        """
        for fragment in self.fragments:
            fragment['node'].removeNode()
            
        self.fragments = []
        self.fragments_node.removeNode()
        self.fragments_node = NodePath("destruction_fragments")
        self.fragments_node.reparentTo(self.game.render)
