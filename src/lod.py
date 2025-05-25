#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sistema de Níveis de Detalhe (LOD) para efeitos visuais no Gorillas 3D War.
Gerencia a complexidade dos efeitos visuais para manter o desempenho.
"""

import time
from enum import Enum

class QualidadeEfeitos(Enum):
    """Enumeração de níveis de qualidade para efeitos visuais."""
    BAIXA = 0
    MEDIA = 1
    ALTA = 2
    ULTRA = 3

class MonitorDesempenho:
    """
    Monitor de desempenho para ajustar dinamicamente a qualidade dos efeitos visuais.
    """
    
    def __init__(self, game, janela_amostras=60, limite_fps_baixo=30, limite_fps_alto=55):
        """
        Inicializa o monitor de desempenho.
        
        Args:
            game: Referência ao objeto principal do jogo.
            janela_amostras: Número de frames para considerar na média de FPS.
            limite_fps_baixo: Limite de FPS abaixo do qual a qualidade será reduzida.
            limite_fps_alto: Limite de FPS acima do qual a qualidade pode ser aumentada.
        """
        self.game = game
        self.janela_amostras = janela_amostras
        self.limite_fps_baixo = limite_fps_baixo
        self.limite_fps_alto = limite_fps_alto
        
        # Histórico de tempos de frame
        self.tempos_frame = []
        self.ultimo_tempo = time.time()
        
        # Contador de frames
        self.contador_frames = 0
        self.tempo_acumulado = 0
        
        # FPS atual
        self.fps_atual = 60.0
        
        # Estatísticas
        self.carga_cpu = 0.0  # Porcentagem de carga da CPU (estimativa)
        self.num_objetos_renderizados = 0
        
        # Regra de reajuste (evita oscilações muito rápidas)
        self.contador_estabilidade = 0
        self.intervalo_ajuste = 5.0  # Segundos entre ajustes de qualidade
        self.ultimo_ajuste = time.time()
    
    def atualizar(self):
        """
        Atualiza as métricas de desempenho.
        
        Returns:
            True se o desempenho está bom, False se precisa de ajustes.
        """
        tempo_atual = time.time()
        dt = tempo_atual - self.ultimo_tempo
        self.ultimo_tempo = tempo_atual
        
        # Adiciona o tempo deste frame
        if dt > 0:
            self.tempos_frame.append(dt)
            
            # Mantém apenas os últimos N frames na janela de amostras
            if len(self.tempos_frame) > self.janela_amostras:
                self.tempos_frame.pop(0)
        
        # Calcula FPS médio
        if self.tempos_frame:
            tempo_medio = sum(self.tempos_frame) / len(self.tempos_frame)
            self.fps_atual = 1.0 / tempo_medio if tempo_medio > 0 else 60.0
        
        # Atualiza estatísticas de renderização
        self.num_objetos_renderizados = len(self.game.render.get_children())
        
        # Estima carga da CPU baseada no FPS 
        # (simplificado - uma implementação real usaria profiling)
        fps_max = 60.0  # Assume 60 como FPS ideal
        self.carga_cpu = min(100.0, (fps_max / max(1.0, self.fps_atual)) * 50.0)
        
        # Verifica se precisa ajustar a qualidade
        precisa_ajuste = False
        tempo_desde_ultimo_ajuste = tempo_atual - self.ultimo_ajuste
        
        if tempo_desde_ultimo_ajuste >= self.intervalo_ajuste:
            if self.fps_atual < self.limite_fps_baixo:
                precisa_ajuste = True
                self.contador_estabilidade = 0
                self.ultimo_ajuste = tempo_atual
            elif self.fps_atual > self.limite_fps_alto:
                self.contador_estabilidade += 1
                if self.contador_estabilidade >= 3:  # 3 intervalos de estabilidade
                    precisa_ajuste = True
                    self.contador_estabilidade = 0
                    self.ultimo_ajuste = tempo_atual
        
        return precisa_ajuste
    
    def obter_fps(self):
        """
        Retorna o FPS atual.
        
        Returns:
            FPS atual.
        """
        return self.fps_atual
    
    def obter_estatisticas(self):
        """
        Retorna as estatísticas de desempenho.
        
        Returns:
            Um dicionário com estatísticas de desempenho.
        """
        return {
            "fps": self.fps_atual,
            "carga_cpu": self.carga_cpu,
            "objetos_renderizados": self.num_objetos_renderizados
        }


class GerenciadorLOD:
    """
    Gerenciador de Níveis de Detalhe (LOD) para efeitos visuais.
    """
    
    def __init__(self, game, qualidade_inicial=QualidadeEfeitos.ALTA):
        """
        Inicializa o gerenciador de LOD.
        
        Args:
            game: Referência ao objeto principal do jogo.
            qualidade_inicial: Qualidade inicial dos efeitos visuais.
        """
        self.game = game
        self.qualidade_atual = qualidade_inicial
        self.monitor = MonitorDesempenho(game)
        
        # Configurações para cada nível de qualidade
        self.configuracoes = {
            QualidadeEfeitos.BAIXA: {
                "max_particulas_explosao": 20,
                "max_particulas_fumaca": 5,
                "max_fragmentos": 10,
                "duracao_efeitos": 0.8,
                "usar_shaders": False,
                "raio_luz": 25,
                "max_luzes": 1,
                "detalhe_modelos": 0.5,
                "max_rastros": 5,
                "distancia_lod": 30
            },
            QualidadeEfeitos.MEDIA: {
                "max_particulas_explosao": 40,
                "max_particulas_fumaca": 10,
                "max_fragmentos": 20,
                "duracao_efeitos": 1.5,
                "usar_shaders": True,
                "raio_luz": 50,
                "max_luzes": 2,
                "detalhe_modelos": 0.75,
                "max_rastros": 10,
                "distancia_lod": 50
            },
            QualidadeEfeitos.ALTA: {
                "max_particulas_explosao": 80,
                "max_particulas_fumaca": 20,
                "max_fragmentos": 40,
                "duracao_efeitos": 2.5,
                "usar_shaders": True,
                "raio_luz": 75,
                "max_luzes": 3,
                "detalhe_modelos": 1.0,
                "max_rastros": 20,
                "distancia_lod": 100
            },
            QualidadeEfeitos.ULTRA: {
                "max_particulas_explosao": 150,
                "max_particulas_fumaca": 30,
                "max_fragmentos": 80,
                "duracao_efeitos": 4.0,
                "usar_shaders": True,
                "raio_luz": 100,
                "max_luzes": 5,
                "detalhe_modelos": 1.5,
                "max_rastros": 40,
                "distancia_lod": 200
            }
        }
        
        # Callbacks para informar quando a qualidade muda
        self.callbacks_mudanca_qualidade = []
    
    def atualizar(self):
        """
        Atualiza o gerenciador de LOD, ajustando a qualidade se necessário.
        """
        # Atualiza o monitor de desempenho
        precisa_ajuste = self.monitor.atualizar()
        
        if precisa_ajuste:
            fps_atual = self.monitor.obter_fps()
            
            # Decide se aumenta ou diminui a qualidade
            if fps_atual < self.monitor.limite_fps_baixo:
                self._diminuir_qualidade()
            elif fps_atual > self.monitor.limite_fps_alto:
                self._aumentar_qualidade()
    
    def _diminuir_qualidade(self):
        """
        Diminui o nível de qualidade dos efeitos visuais.
        """
        if self.qualidade_atual.value > QualidadeEfeitos.BAIXA.value:
            nova_qualidade = QualidadeEfeitos(self.qualidade_atual.value - 1)
            self._aplicar_nova_qualidade(nova_qualidade)
            print(f"Desempenho baixo detectado. Reduzindo qualidade para: {nova_qualidade.name}")
    
    def _aumentar_qualidade(self):
        """
        Aumenta o nível de qualidade dos efeitos visuais.
        """
        if self.qualidade_atual.value < QualidadeEfeitos.ULTRA.value:
            nova_qualidade = QualidadeEfeitos(self.qualidade_atual.value + 1)
            self._aplicar_nova_qualidade(nova_qualidade)
            print(f"Desempenho bom detectado. Aumentando qualidade para: {nova_qualidade.name}")
    
    def _aplicar_nova_qualidade(self, nova_qualidade):
        """
        Aplica o novo nível de qualidade.
        
        Args:
            nova_qualidade: Novo nível de qualidade a ser aplicado.
        """
        antiga_qualidade = self.qualidade_atual
        self.qualidade_atual = nova_qualidade
        
        # Notifica os callbacks registrados
        for callback in self.callbacks_mudanca_qualidade:
            callback(antiga_qualidade, nova_qualidade, self.configuracoes[nova_qualidade])
    
    def registrar_callback_mudanca_qualidade(self, callback):
        """
        Registra um callback para ser chamado quando a qualidade mudar.
        
        Args:
            callback: Função a ser chamada quando a qualidade mudar.
                     Deve aceitar 3 parâmetros: qualidade_antiga, qualidade_nova, configuracoes
        """
        if callback not in self.callbacks_mudanca_qualidade:
            self.callbacks_mudanca_qualidade.append(callback)
    
    def definir_qualidade(self, qualidade):
        """
        Define manualmente o nível de qualidade.
        
        Args:
            qualidade: Novo nível de qualidade (QualidadeEfeitos).
        """
        if qualidade != self.qualidade_atual:
            self._aplicar_nova_qualidade(qualidade)
    
    def obter_configuracoes_atuais(self):
        """
        Retorna as configurações para o nível de qualidade atual.
        
        Returns:
            Dicionário com as configurações atuais.
        """
        return self.configuracoes[self.qualidade_atual]
    
    def obter_qualidade_atual(self):
        """
        Retorna o nível de qualidade atual.
        
        Returns:
            Nível de qualidade atual (QualidadeEfeitos).
        """
        return self.qualidade_atual
