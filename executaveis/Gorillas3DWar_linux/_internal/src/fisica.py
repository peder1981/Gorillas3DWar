#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sistema de física para o jogo Gorillas 3D War.
Gerencia a interação física entre objetos, explosões e o ambiente.
"""

from panda3d.core import NodePath, LVector3, LPoint3, BitMask32
from panda3d.bullet import BulletWorld, BulletRigidBodyNode, BulletSphereShape
from panda3d.bullet import BulletBoxShape, BulletCylinderShape, BulletDebugNode
import math
import random

class SistemaFisica:
    """
    Sistema de física que gerencia colisões e forças no jogo Gorillas 3D War.
    Utiliza o sistema Bullet Physics do Panda3D.
    """
    
    def __init__(self, game):
        """
        Inicializa o sistema de física.
        
        Args:
            game: Referência ao objeto principal do jogo.
        """
        self.game = game
        
        # Cria o mundo de física
        self.mundo_fisica = BulletWorld()
        self.mundo_fisica.setGravity(LVector3(0, 0, -9.81))  # Gravidade padrão
        
        # Nó para visualização de depuração da física (quando ativado)
        self.debug_node = self.game.render.attachNewNode(BulletDebugNode('Debug'))
        self.debug_node.node().showWireframe(True)
        self.debug_node.node().showConstraints(True)
        self.debug_node.node().showBoundingBoxes(False)
        self.debug_node.node().showNormals(False)
        self.debug_node.hide()  # Inicialmente escondido
        
        # Categorias de colisão
        self.categorias = {
            'terreno': BitMask32.bit(0),
            'predios': BitMask32.bit(1),
            'gorillas': BitMask32.bit(2),
            'projeteis': BitMask32.bit(3),
            'fragmentos': BitMask32.bit(4),
            'objetos_destrutiveis': BitMask32.bit(5)
        }
        
        # Lista de corpos físicos
        self.corpos_fisicos = []
        
        # Lista de corpos temporários (como fragmentos de explosão)
        self.corpos_temporarios = []
        
        # Objetos afetados por explosões recentes
        self.objetos_afetados = set()
        
        # Tempo máximo de vida para objetos temporários (segundos)
        self.tempo_vida_temporarios = 10.0
        
        # Distância máxima de efeito para explosões
        self.distancia_maxima_explosao = 20.0
        
        # Configurações de resposta a colisões
        self.coeficiente_restituicao = 0.3  # Elasticidade das colisões
        
        # Callbacks para eventos de colisão
        self.callbacks_colisao = []
    
    def atualizar(self, dt):
        """
        Atualiza o sistema de física.
        
        Args:
            dt: Delta time (tempo desde o último frame).
        """
        # Atualiza a simulação de física
        self.mundo_fisica.doPhysics(dt)
        
        # Atualiza corpos temporários e remove os expirados
        self._atualizar_corpos_temporarios(dt)
        
        # Processa colisões pendentes
        self._processar_colisoes()
    
    def _atualizar_corpos_temporarios(self, dt):
        """
        Atualiza corpos temporários e remove os expirados.
        
        Args:
            dt: Delta time (tempo desde o último frame).
        """
        # Atualiza e remove corpos temporários expirados
        for corpo in list(self.corpos_temporarios):
            corpo['tempo_vida'] -= dt
            
            # Remove corpos expirados
            if corpo['tempo_vida'] <= 0:
                self._remover_corpo_fisico(corpo['node'])
                self.corpos_temporarios.remove(corpo)
    
    def _processar_colisoes(self):
        """
        Processa as colisões que ocorreram no último frame.
        """
        # Obtém o manifold de colisões
        for contato in self.mundo_fisica.getContactManifolds():
            node0 = contato.getNode0()
            node1 = contato.getNode1()
            
            # Verifica se há pontos de contato
            if contato.getNumManifoldPoints() > 0:
                # Obtém informações do primeiro ponto de contato
                ponto = contato.getManifoldPoint(0)
                posicao = ponto.getPositionWorldOnB()
                normal = ponto.getNormalWorldOnB()
                impulso = ponto.getAppliedImpulse()
                
                # Dispara callbacks de colisão
                for callback in self.callbacks_colisao:
                    callback(node0, node1, posicao, normal, impulso)
    
    def aplicar_forca_explosao(self, posicao, raio, forca, afetar_predios=True):
        """
        Aplica força radial de explosão a todos os objetos físicos dentro do raio.
        
        Args:
            posicao: Posição da explosão (LPoint3).
            raio: Raio de efeito da explosão.
            forca: Magnitude da força da explosão.
            afetar_predios: Se True, a explosão também afeta prédios.
        
        Returns:
            Lista de objetos afetados pela explosão.
        """
        objetos_afetados = []
        
        # Limita o raio ao máximo configurado
        raio_efetivo = min(raio, self.distancia_maxima_explosao)
        
        # Verifica cada corpo físico
        for corpo in self.corpos_fisicos:
            node = corpo['node']
            
            # Pula prédios se não for para afetá-los
            if not afetar_predios and 'predio' in corpo['tags']:
                continue
            
            # Pula objetos estáticos
            if not node.isStatic():
                # Calcula a distância
                pos_obj = node.getPos(self.game.render)
                vetor = pos_obj - posicao
                distancia = vetor.length()
                
                # Se estiver dentro do raio de efeito
                if distancia < raio_efetivo:
                    # Normaliza o vetor de direção
                    if distancia > 0.1:
                        direcao = vetor / distancia
                    else:
                        # Se muito próximo, usa direção aleatória
                        direcao = LVector3(
                            random.uniform(-1, 1),
                            random.uniform(-1, 1),
                            random.uniform(0.5, 1)
                        ).normalize()
                    
                    # Calcula a força baseada na distância (quanto mais próximo, maior a força)
                    fator_distancia = 1.0 - (distancia / raio_efetivo)
                    forca_aplicada = forca * fator_distancia
                    
                    # Adiciona componente vertical para criar efeito de "lançamento"
                    direcao.z += 0.5
                    direcao.normalize()
                    
                    # Aplica impulso ao corpo
                    node.node().applyImpulse(direcao * forca_aplicada, LPoint3(0, 0, 0))
                    
                    # Adiciona torque aleatório para girar o objeto
                    torque = LVector3(
                        random.uniform(-1, 1) * forca_aplicada * 0.5,
                        random.uniform(-1, 1) * forca_aplicada * 0.5,
                        random.uniform(-1, 1) * forca_aplicada * 0.5
                    )
                    node.node().applyTorqueImpulse(torque)
                    
                    # Adiciona à lista de objetos afetados
                    objetos_afetados.append({
                        'node': node,
                        'distancia': distancia,
                        'forca': forca_aplicada
                    })
                    
                    # Marca como afetado por explosão recente
                    self.objetos_afetados.add(node)
        
        return objetos_afetados
    
    def criar_fragmentos_explosao(self, posicao, modelo, num_fragmentos, forca, escala_fragmentos=0.5, tempo_vida=5.0):
        """
        Cria fragmentos físicos para uma explosão.
        
        Args:
            posicao: Posição para criar os fragmentos.
            modelo: Modelo a ser usado para os fragmentos.
            num_fragmentos: Número de fragmentos a criar.
            forca: Força da explosão.
            escala_fragmentos: Escala dos fragmentos.
            tempo_vida: Tempo de vida dos fragmentos em segundos.
        
        Returns:
            Lista de nodes dos fragmentos criados.
        """
        fragmentos = []
        
        for i in range(num_fragmentos):
            # Cria forma física baseada no tipo de fragmento
            tipo_forma = random.choice(['box', 'sphere', 'cylinder'])
            
            if tipo_forma == 'box':
                tamanho = random.uniform(0.1, 0.3) * escala_fragmentos
                forma = BulletBoxShape(LVector3(tamanho, tamanho, tamanho))
            elif tipo_forma == 'sphere':
                raio = random.uniform(0.1, 0.25) * escala_fragmentos
                forma = BulletSphereShape(raio)
            else:  # cylinder
                raio = random.uniform(0.1, 0.2) * escala_fragmentos
                altura = random.uniform(0.2, 0.4) * escala_fragmentos
                forma = BulletCylinderShape(raio, altura, 1)  # 1 = eixo Z
            
            # Cria nó físico
            corpo_node = BulletRigidBodyNode(f'fragmento_{i}')
            corpo_node.addShape(forma)
            
            # Define massa (afeta a inércia)
            massa = random.uniform(0.1, 1.0) * escala_fragmentos
            corpo_node.setMass(massa)
            
            # Define coeficiente de restituição (elasticidade)
            corpo_node.setRestitution(self.coeficiente_restituicao)
            
            # Define atrito
            corpo_node.setFriction(0.8)
            
            # Define categorias de colisão
            corpo_node.setIntoCollideMask(self.categorias['fragmentos'])
            corpo_node.setFromCollideMask(self.categorias['terreno'] | self.categorias['predios'])
            
            # Cria e posiciona o node visual
            fragmento_np = self.game.render.attachNewNode(corpo_node)
            fragmento_np.setPos(posicao)
            
            # Adiciona variação à posição
            offset = LVector3(
                random.uniform(-0.5, 0.5),
                random.uniform(-0.5, 0.5),
                random.uniform(0, 1.0)
            )
            fragmento_np.setPos(posicao + offset * escala_fragmentos)
            
            # Rotação aleatória
            fragmento_np.setHpr(
                random.uniform(0, 360),
                random.uniform(0, 360),
                random.uniform(0, 360)
            )
            
            # Escala aleatória
            variacao_escala = random.uniform(0.8, 1.2)
            fragmento_np.setScale(escala_fragmentos * variacao_escala)
            
            # Copia o modelo para o fragmento
            modelo_fragmento = self.game.loader.loadModel(modelo)
            modelo_fragmento.reparentTo(fragmento_np)
            
            # Aplica materiais aleatórios (cor e textura)
            r, g, b = random.uniform(0.3, 0.8), random.uniform(0.3, 0.7), random.uniform(0.3, 0.6)
            modelo_fragmento.setColor(r, g, b, 1)
            
            # Adiciona o corpo ao mundo físico
            self.mundo_fisica.attachRigidBody(corpo_node)
            
            # Aplica impulso inicial (força da explosão)
            direcao = LVector3(
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                random.uniform(0.5, 1.5)
            ).normalize()
            
            forca_fragmento = forca * random.uniform(0.5, 1.5) * (1.0 / massa)
            corpo_node.applyImpulse(direcao * forca_fragmento, LPoint3(0, 0, 0))
            
            # Aplica torque aleatório
            torque = LVector3(
                random.uniform(-1, 1) * forca_fragmento * 0.5,
                random.uniform(-1, 1) * forca_fragmento * 0.5,
                random.uniform(-1, 1) * forca_fragmento * 0.5
            )
            corpo_node.applyTorqueImpulse(torque)
            
            # Adiciona à lista de fragmentos e corpos temporários
            fragmentos.append(fragmento_np)
            
            # Adiciona aos corpos temporários para remoção automática
            self.corpos_temporarios.append({
                'node': fragmento_np,
                'tempo_vida': tempo_vida,
                'tempo_inicial': tempo_vida,
                'tipo': 'fragmento'
            })
            
            # Adiciona à lista geral de corpos
            self.corpos_fisicos.append({
                'node': fragmento_np,
                'tags': ['fragmento', 'temporario'],
                'nome': f'fragmento_{i}'
            })
        
        return fragmentos
    
    def criar_corpo_fisico(self, node_path, massa, forma, categoria, nome, tags=None, e_estatico=False):
        """
        Cria um corpo físico para um NodePath.
        
        Args:
            node_path: NodePath ao qual adicionar o corpo físico.
            massa: Massa do corpo (0 = estático).
            forma: Forma física (BulletShape).
            categoria: Categoria de colisão.
            nome: Nome para o corpo físico.
            tags: Lista de tags para categorizar o corpo.
            e_estatico: Se True, o corpo é estático (não se move).
        
        Returns:
            NodePath do corpo físico criado.
        """
        if tags is None:
            tags = []
        
        # Cria o nó para o corpo físico
        corpo_node = BulletRigidBodyNode(nome)
        corpo_node.addShape(forma)
        
        # Configura propriedades físicas
        if e_estatico:
            corpo_node.setMass(0)  # Massa 0 = estático
        else:
            corpo_node.setMass(massa)
        
        corpo_node.setRestitution(self.coeficiente_restituicao)
        corpo_node.setFriction(0.8)
        
        # Define categorias de colisão
        corpo_node.setIntoCollideMask(self.categorias[categoria])
        
        # Define contra quais categorias colide
        mascara_colisao = BitMask32(0)
        for cat, mask in self.categorias.items():
            if cat != categoria:  # Não colide com objetos da mesma categoria
                mascara_colisao |= mask
        
        corpo_node.setFromCollideMask(mascara_colisao)
        
        # Cria o NodePath para o corpo físico
        corpo_np = node_path.attachNewNode(corpo_node)
        corpo_np.setPos(0, 0, 0)  # Posição relativa ao nó pai
        
        # Adiciona o corpo ao mundo físico
        self.mundo_fisica.attachRigidBody(corpo_node)
        
        # Registra o corpo
        self.corpos_fisicos.append({
            'node': corpo_np,
            'tags': tags,
            'nome': nome
        })
        
        return corpo_np
    
    def _remover_corpo_fisico(self, node_path):
        """
        Remove um corpo físico do mundo e da lista.
        
        Args:
            node_path: NodePath do corpo a remover.
        """
        # Remove do mundo físico
        if node_path.node() and isinstance(node_path.node(), BulletRigidBodyNode):
            self.mundo_fisica.removeRigidBody(node_path.node())
        
        # Remove da lista de corpos
        for corpo in list(self.corpos_fisicos):
            if corpo['node'] == node_path:
                self.corpos_fisicos.remove(corpo)
                break
        
        # Remove da lista de corpos temporários
        for corpo in list(self.corpos_temporarios):
            if corpo['node'] == node_path:
                self.corpos_temporarios.remove(corpo)
                break
        
        # Remove da lista de objetos afetados
        if node_path in self.objetos_afetados:
            self.objetos_afetados.remove(node_path)
        
        # Remove o NodePath
        node_path.removeNode()
    
    def remover_todos_corpos(self):
        """
        Remove todos os corpos físicos.
        """
        # Remove todos os corpos do mundo físico
        for corpo in list(self.corpos_fisicos):
            self._remover_corpo_fisico(corpo['node'])
        
        # Limpa as listas
        self.corpos_fisicos = []
        self.corpos_temporarios = []
        self.objetos_afetados.clear()
    
    def registrar_callback_colisao(self, callback):
        """
        Registra um callback para eventos de colisão.
        
        Args:
            callback: Função a ser chamada quando ocorrer uma colisão.
                     Deve aceitar os parâmetros: node1, node2, posicao, normal, impulso
        """
        if callback not in self.callbacks_colisao:
            self.callbacks_colisao.append(callback)
    
    def ativar_depuracao(self, ativo=True):
        """
        Ativa ou desativa a visualização de depuração da física.
        
        Args:
            ativo: Se True, ativa a visualização.
        """
        if ativo:
            self.mundo_fisica.setDebugNode(self.debug_node.node())
            self.debug_node.show()
        else:
            self.debug_node.hide()
    
    def alterar_gravidade(self, gravidade):
        """
        Altera a gravidade do mundo físico.
        
        Args:
            gravidade: Vetor de gravidade (LVector3).
        """
        self.mundo_fisica.setGravity(gravidade)
    
    def definir_coeficiente_restituicao(self, valor):
        """
        Define o coeficiente de restituição (elasticidade) padrão.
        
        Args:
            valor: Valor entre 0 (sem elasticidade) e 1 (altamente elástico).
        """
        self.coeficiente_restituicao = max(0.0, min(1.0, valor))
        
        # Atualiza corpos existentes
        for corpo in self.corpos_fisicos:
            node = corpo['node']
            if isinstance(node.node(), BulletRigidBodyNode):
                node.node().setRestitution(self.coeficiente_restituicao)
