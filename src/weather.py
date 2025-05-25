#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gorillas 3D War - Módulo de sistema de clima
"""
from panda3d.core import NodePath, TextureStage, Texture
from panda3d.core import Point3, Vec3, ColorBlendAttrib
from direct.particles.ParticleEffect import ParticleEffect
import random
import math

class WeatherSystem:
    """
    Sistema de clima para o jogo, incluindo chuva, neve, neblina e outros efeitos climáticos.
    """
    def __init__(self, game):
        """
        Inicializa o sistema de clima.
        
        Args:
            game: Referência ao jogo principal.
        """
        self.game = game
        
        # Nó principal para todos os efeitos de clima
        self.weather_node = NodePath("weather_effects")
        self.weather_node.reparentTo(game.render)
        
        # Tipo de clima atual
        # Valores possíveis: 'limpo', 'chuva', 'neve', 'neblina', 'tempestade'
        self.clima_atual = 'limpo'
        
        # Intensidade do clima (0.0 a 1.0)
        self.intensidade = 0.0
        
        # Efeitos de partículas para diferentes climas
        self.particulas = {}
        
        # Nó de neblina
        self.neblina_node = None
        
        # Tempo para próximo trovão (para clima de tempestade)
        self.tempo_proximo_trovao = 0
        
        # Configuração inicial
        self.configurar_sistema()
        
    def configurar_sistema(self):
        """
        Configura o sistema de clima, preparando os diferentes efeitos.
        """
        # Configura efeitos de partículas
        self.configurar_particulas_chuva()
        self.configurar_particulas_neve()
        
        # Configura neblina
        self.configurar_neblina()
        
    def configurar_particulas_chuva(self):
        """
        Configura o efeito de partículas para chuva.
        """
        # Cria um efeito de partículas para chuva
        chuva = ParticleEffect()
        
        # Em uma implementação real, carregaríamos a configuração de um arquivo
        # Como não temos acesso aos arquivos, vamos configurar manualmente
        
        # Criamos um gerador de partículas básico
        p0 = chuva.createParticleEffect()
        p0.setFactory("PointParticleFactory")
        p0.setRenderer("LineParticleRenderer")
        p0.setEmitter("BoxEmitter")
        
        # Configurações básicas
        p0.getFactory().setLifespanBase(0.5)
        p0.getFactory().setLifespanSpread(0.2)
        p0.getFactory().setMassBase(1.0)
        p0.getFactory().setMassSpread(0.0)
        
        # Configurações do renderizador
        p0.getRenderer().setAlphaMode(BaseParticleRenderer.PRALPHANONE)
        p0.getRenderer().setUserAlpha(0.3)
        
        # Configura a linha para parecer gotas de chuva
        l = p0.getRenderer()
        l.setHeadColor(Vec4(0.5, 0.5, 1.0, 1.0))
        l.setTailColor(Vec4(0.3, 0.3, 1.0, 0.0))
        l.setLineScaleFactor(2.0)
        
        # Configurações do emissor
        e = p0.getEmitter()
        e.setEmissionType(BaseParticleEmitter.ETRADIATE)
        e.setAmplitude(1.0)
        e.setAmplitudeSpread(0.0)
        e.setOffsetForce(Vec3(0.0, 0.0, -10.0))
        e.setExplicitLaunchVector(Vec3(0.0, 0.0, -10.0))
        e.setRadiateOrigin(Point3(0.0, 0.0, 20.0))
        
        # Configura a caixa do emissor
        e.setMinBound(Point3(-50.0, -50.0, 20.0))
        e.setMaxBound(Point3(50.0, 50.0, 20.0))
        
        # Armazena o efeito
        self.particulas['chuva'] = chuva
        
    def configurar_particulas_neve(self):
        """
        Configura o efeito de partículas para neve.
        """
        # Cria um efeito de partículas para neve
        neve = ParticleEffect()
        
        # Em uma implementação real, carregaríamos a configuração de um arquivo
        # Como não temos acesso aos arquivos, vamos configurar manualmente
        
        # Criamos um gerador de partículas básico
        p0 = neve.createParticleEffect()
        p0.setFactory("PointParticleFactory")
        p0.setRenderer("SpriteParticleRenderer")
        p0.setEmitter("BoxEmitter")
        
        # Configurações básicas
        p0.getFactory().setLifespanBase(3.0)
        p0.getFactory().setLifespanSpread(0.5)
        p0.getFactory().setMassBase(1.0)
        p0.getFactory().setMassSpread(0.0)
        
        # Configurações do renderizador
        p0.getRenderer().setAlphaMode(BaseParticleRenderer.PRALPHANONE)
        p0.getRenderer().setUserAlpha(0.8)
        
        # Configura o sprite para ser um floco de neve
        # Idealmente, carregaríamos uma textura de floco de neve
        s = p0.getRenderer()
        s.setColor(Vec4(1.0, 1.0, 1.0, 1.0))
        s.setXScaleFlag(1)
        s.setYScaleFlag(1)
        s.setAnimAngleFlag(0)
        s.setInitialXScale(0.05)
        s.setFinalXScale(0.05)
        s.setInitialYScale(0.05)
        s.setFinalYScale(0.05)
        
        # Configurações do emissor
        e = p0.getEmitter()
        e.setEmissionType(BaseParticleEmitter.ETRADIATE)
        e.setAmplitude(1.0)
        e.setAmplitudeSpread(0.0)
        e.setOffsetForce(Vec3(0.0, 0.0, -1.0))
        e.setExplicitLaunchVector(Vec3(0.0, 0.0, -1.0))
        e.setRadiateOrigin(Point3(0.0, 0.0, 20.0))
        
        # Configura a caixa do emissor
        e.setMinBound(Point3(-50.0, -50.0, 20.0))
        e.setMaxBound(Point3(50.0, 50.0, 20.0))
        
        # Armazena o efeito
        self.particulas['neve'] = neve
        
    def configurar_neblina(self):
        """
        Configura o efeito de neblina.
        """
        # Cria um nó para a neblina
        self.neblina_node = NodePath("neblina")
        self.neblina_node.reparentTo(self.weather_node)
        
        # Cria um plano com textura semitransparente
        cm = CardMaker('neblina_card')
        cm.setFrame(-100, 100, -100, 100)
        
        # Cria várias camadas de neblina em diferentes alturas
        for i in range(5):
            altura = i * 10
            neblina = self.neblina_node.attachNewNode(cm.generate())
            neblina.setPos(0, 0, altura)
            neblina.setP(-90)  # Torna horizontal
            neblina.setTransparency(TransparencyAttrib.MAlpha)
            neblina.setColor(0.7, 0.7, 0.8, 0.1)  # Cor cinza azulada semitransparente
            neblina.setBin('fixed', 0)  # Para renderizar corretamente a transparência
            
        # Esconde a neblina inicialmente
        self.neblina_node.hide()
        
    def definir_clima(self, tipo, intensidade=0.5, transicao=True):
        """
        Define o clima atual.
        
        Args:
            tipo: Tipo de clima ('limpo', 'chuva', 'neve', 'neblina', 'tempestade').
            intensidade: Intensidade do clima, de 0.0 a 1.0.
            transicao: Se True, faz uma transição suave.
        """
        # Armazena os valores
        self.clima_anterior = self.clima_atual
        self.clima_atual = tipo
        self.intensidade_anterior = self.intensidade
        self.intensidade = max(0.0, min(1.0, intensidade))
        
        # Se não quiser transição, aplica imediatamente
        if not transicao:
            self.aplicar_clima(tipo, self.intensidade)
            return
            
        # Configura para fazer a transição gradual
        self.transicao_tempo = 0.0
        self.transicao_duracao = 2.0  # segundos
        
        # Adiciona uma tarefa para fazer a transição
        self.game.taskMgr.add(self.atualizar_transicao_clima, "transicao_clima")
        
    def aplicar_clima(self, tipo, intensidade):
        """
        Aplica um clima específico com a intensidade especificada.
        
        Args:
            tipo: Tipo de clima ('limpo', 'chuva', 'neve', 'neblina', 'tempestade').
            intensidade: Intensidade do clima, de 0.0 a 1.0.
        """
        # Desativa todos os efeitos primeiro
        self.desativar_todos_efeitos()
        
        # Aplica o efeito conforme o tipo
        if tipo == 'limpo':
            # Nada a fazer, todos os efeitos já foram desativados
            pass
            
        elif tipo == 'chuva':
            # Ativa o efeito de chuva
            if 'chuva' in self.particulas:
                particula = self.particulas['chuva']
                particula.start(self.weather_node)
                
                # Ajusta a intensidade
                p0 = particula.getParticlesNamed('particles-1')
                p0.getEmitter().setAmplitude(intensidade * 2.0)
                
                # Inicia o som de chuva
                if hasattr(self.game, 'som'):
                    self.game.som.iniciar_som_ambiente('chuva')
                    self.game.som.tocar_som('chuva', volume=intensidade * 0.8)
                
        elif tipo == 'neve':
            # Ativa o efeito de neve
            if 'neve' in self.particulas:
                particula = self.particulas['neve']
                particula.start(self.weather_node)
                
                # Ajusta a intensidade
                p0 = particula.getParticlesNamed('particles-1')
                p0.getEmitter().setAmplitude(intensidade * 2.0)
                
        elif tipo == 'neblina':
            # Ativa o efeito de neblina
            if self.neblina_node:
                self.neblina_node.show()
                
                # Ajusta a intensidade (opacidade)
                for i, node in enumerate(self.neblina_node.getChildren()):
                    node.setAlphaScale(intensidade * 0.2)
                
        elif tipo == 'tempestade':
            # Combina chuva com relâmpagos
            # Ativa o efeito de chuva intenso
            if 'chuva' in self.particulas:
                particula = self.particulas['chuva']
                particula.start(self.weather_node)
                
                # Ajusta para chuva intensa
                p0 = particula.getParticlesNamed('particles-1')
                p0.getEmitter().setAmplitude(intensidade * 3.0)
                
                # Inicia o som de chuva forte
                if hasattr(self.game, 'som'):
                    self.game.som.iniciar_som_ambiente('chuva')
                    self.game.som.tocar_som('chuva', volume=intensidade * 1.0)
                
                # Configura para gerar relâmpagos periodicamente
                self.tempo_proximo_trovao = random.uniform(5.0, 15.0)
                
                # Adiciona uma tarefa para controlar os relâmpagos
                self.game.taskMgr.add(self.atualizar_tempestade, "tempestade")
                
        # Atualiza os parâmetros físicos do jogo com base no clima
        self.atualizar_parametros_fisicos()
                
    def desativar_todos_efeitos(self):
        """
        Desativa todos os efeitos de clima.
        """
        # Para todas as partículas
        for particula in self.particulas.values():
            particula.disable()
            
        # Esconde a neblina
        if self.neblina_node:
            self.neblina_node.hide()
            
        # Remove tarefas de clima
        self.game.taskMgr.remove("tempestade")
        
        # Para sons de ambiente
        if hasattr(self.game, 'som'):
            self.game.som.parar_som_ambiente('chuva')
            self.game.som.parar_som_ambiente('vento')
            
    def atualizar_transicao_clima(self, task):
        """
        Atualiza a transição entre climas.
        """
        # Incrementa o tempo
        self.transicao_tempo += self.game.taskMgr.globalClock.getDt()
        
        # Calcula o progresso da transição (0.0 a 1.0)
        progress = min(1.0, self.transicao_tempo / self.transicao_duracao)
        
        # Calcula a intensidade atual interpolada
        intensidade_atual = self.intensidade_anterior + (self.intensidade - self.intensidade_anterior) * progress
        
        # Aplica o clima com a intensidade atual
        if progress < 0.5:
            # Primeira metade: desativa o clima anterior gradualmente
            self.aplicar_clima(self.clima_anterior, intensidade_atual * (1.0 - progress * 2))
        else:
            # Segunda metade: ativa o novo clima gradualmente
            self.aplicar_clima(self.clima_atual, intensidade_atual * (progress * 2 - 1.0))
        
        # Verifica se a transição terminou
        if progress >= 1.0:
            self.aplicar_clima(self.clima_atual, self.intensidade)
            return task.done
            
        return task.cont
        
    def atualizar_tempestade(self, task):
        """
        Atualiza os efeitos de tempestade, como relâmpagos.
        """
        # Verifica se o clima atual ainda é tempestade
        if self.clima_atual != 'tempestade':
            return task.done
            
        # Decrementa o tempo para o próximo trovão
        self.tempo_proximo_trovao -= self.game.taskMgr.globalClock.getDt()
        
        # Se for hora de um relâmpago
        if self.tempo_proximo_trovao <= 0:
            # Cria um flash de luz
            self.criar_relampago()
            
            # Toca o som de trovão
            if hasattr(self.game, 'som'):
                self.game.som.tocar_som('trovao', volume=self.intensidade * 0.9)
                
            # Define o tempo para o próximo trovão
            self.tempo_proximo_trovao = random.uniform(5.0, 15.0) * (1.0 / self.intensidade)
            
        return task.cont
        
    def criar_relampago(self):
        """
        Cria um efeito de relâmpago (flash de luz).
        """
        # Aumenta temporariamente a luz ambiente
        if hasattr(self.game, 'luzes') and 'ambiente' in self.game.luzes:
            luz_ambiente = self.game.luzes['ambiente'].getNode()
            cor_original = luz_ambiente.getColor()
            
            # Cria uma sequência para o flash
            from direct.interval.LerpInterval import LerpColorInterval
            from direct.interval.MetaInterval import Sequence
            
            # Flash rápido
            seq = Sequence(
                LerpColorInterval(luz_ambiente, 0.1, (1, 1, 1, 1)),  # Luz intensa
                LerpColorInterval(luz_ambiente, 0.3, cor_original)   # Volta ao normal
            )
            seq.start()
            
    def atualizar_parametros_fisicos(self):
        """
        Atualiza os parâmetros físicos do jogo com base no clima atual.
        """
        # Ajusta o vento com base no clima
        if self.clima_atual in ['chuva', 'tempestade']:
            # Aumenta o vento em climas chuvosos/tempestuosos
            fator_vento = 1.0 + self.intensidade * 2.0
            self.game.vento = self.game.vento * fator_vento
            
            # Inicia o som de vento
            if hasattr(self.game, 'som'):
                self.game.som.iniciar_som_ambiente('vento')
                self.game.som.tocar_som('vento', volume=self.intensidade * 0.6)
                
        # Ajusta a gravidade e resistência do ar com base no clima
        if self.clima_atual == 'neve':
            # Neve reduz a gravidade efetiva (aumenta resistência do ar)
            fator_gravidade = 1.0 - self.intensidade * 0.3
            self.game.gravidade = self.game.gravidade * fator_gravidade
            
    def atualizar(self):
        """
        Atualiza os efeitos de clima a cada frame.
        """
        # Atualiza a posição dos efeitos de clima para seguir a câmera
        # Isso mantém os efeitos sempre em torno do jogador
        camera_pos = self.game.camera.getPos()
        self.weather_node.setPos(camera_pos.getX(), camera_pos.getY(), 0)
        
    def clima_aleatorio(self):
        """
        Define um clima aleatório.
        
        Returns:
            Tupla com o tipo de clima e intensidade escolhidos.
        """
        # Lista de climas possíveis e suas probabilidades
        climas = [
            ('limpo', 0.4),      # 40% de chance de tempo limpo
            ('chuva', 0.25),     # 25% de chance de chuva
            ('neve', 0.15),      # 15% de chance de neve
            ('neblina', 0.1),    # 10% de chance de neblina
            ('tempestade', 0.1)  # 10% de chance de tempestade
        ]
        
        # Escolhe um clima baseado nas probabilidades
        tipo = random.choices([c[0] for c in climas], weights=[c[1] for c in climas], k=1)[0]
        
        # Escolhe uma intensidade aleatória
        intensidade = random.uniform(0.3, 1.0)
        
        # Define o clima
        self.definir_clima(tipo, intensidade)
        
        return (tipo, intensidade)
        
    def limpar(self):
        """
        Limpa todos os recursos alocados pelo sistema de clima.
        """
        self.desativar_todos_efeitos()
        
        # Remove nós
        if self.neblina_node:
            self.neblina_node.removeNode()
            self.neblina_node = None
            
        self.weather_node.removeNode()
