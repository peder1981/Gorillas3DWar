#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gorillas 3D War - Módulo principal do jogo
"""
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectFrame, DirectButton, DirectSlider, DirectLabel
from panda3d.core import TextNode, TransparencyAttrib, LPoint3, LineSegs
from panda3d.core import CollisionTraverser, CollisionHandlerQueue
from panda3d.core import WindowProperties, AmbientLight, DirectionalLight
from panda3d.core import LVector3, NodePath, TextureStage, Texture
import sys
import os
import math
import random
import numpy as np
from src.city import CityGenerator
from src.gorilla import Gorilla
from src.projectile import Banana
from src.effects import ExplosionManager
from src.camera import GameCamera
from src.ui import GameUI
from src.sound import SoundManager
from src.weather import WeatherSystem
from src.destruction import DestructionSystem

class Gorillas3DWar(ShowBase):
    """
    Classe principal do jogo Gorillas 3D War.
    Gerencia todo o ciclo de vida do jogo, incluindo inicialização,
    loop principal, eventos de entrada e estados do jogo.
    """
    def __init__(self):
        """
        Inicializa o jogo, configurando a janela, luzes, câmera,
        cidade, gorilas e outros elementos do jogo.
        """
        # Inicializa a classe base ShowBase do Panda3D
        ShowBase.__init__(self)
        
        # Configurações da janela
        self.configurar_janela()
        
        # Configuração do sistema de colisão
        self.configurar_colisoes()
        
        # Configuração das luzes
        self.configurar_luzes()
        
        # Cria o céu
        self.criar_ceu()
        
        # Estado do jogo: 'menu', 'jogando', 'game_over'
        self.estado_jogo = 'menu'
        
        # Parâmetros do jogo
        self.configurar_parametros_jogo()
        
        # Gera a cidade
        self.gerador_cidade = CityGenerator(self)
        self.cidade = self.gerador_cidade.gerar_cidade(7, 7)
        
        # Configura a câmera e controles
        self.camera_jogo = GameCamera(self)
        
        # Cria os gorilas
        self.criar_gorilas()
        
        # Inicializa os sistemas do jogo
        self.inicializar_sistemas()
        
        # Interface do usuário
        self.ui = GameUI(self)
        
        # Configura as tarefas
        self.configurar_tarefas()
        
        # Configura os eventos de entrada
        self.configurar_eventos()
        
        # Inicia a música de fundo
        self.som.tocar_musica('menu')
        
        # Mostra o menu principal
        self.mostrar_menu_principal()

    def configurar_janela(self):
        """
        Configura as propriedades da janela do jogo.
        """
        props = WindowProperties()
        props.setTitle("Gorillas 3D War")
        props.setSize(1280, 720)
        self.win.requestProperties(props)
        
        # Desabilita os controles padrão de câmera do Panda3D
        self.disableMouse()
        
        # Configura a cor de fundo
        self.setBackgroundColor(0.5, 0.7, 1.0)

    def configurar_colisoes(self):
        """
        Configura o sistema de colisões do jogo.
        """
        self.cTrav = CollisionTraverser('traverser')
        self.collisionHandler = CollisionHandlerQueue()

    def configurar_luzes(self):
        """
        Configura as luzes para a cena 3D.
        """
        # Luz ambiente (luz geral)
        alight = AmbientLight('alight')
        alight.setColor((0.4, 0.4, 0.4, 1))
        alightNP = self.render.attachNewNode(alight)
        self.render.setLight(alightNP)
        
        # Luz direcional (como o sol)
        dlight = DirectionalLight('dlight')
        dlight.setColor((0.8, 0.8, 0.7, 1))
        dlightNP = self.render.attachNewNode(dlight)
        dlightNP.setHpr(60, -60, 0)  # Direção da luz
        self.render.setLight(dlightNP)
        
        # Guarda referências para poder ajustar depois
        self.luzes = {
            'ambiente': alightNP,
            'direcional': dlightNP
        }

    def criar_ceu(self):
        """
        Cria o céu usando uma esfera com textura.
        """
        # Criamos uma grande esfera para simular o céu
        # Seria necessário ter um arquivo de textura para o céu
        # Por enquanto usamos apenas a cor de fundo
        pass

    def configurar_parametros_jogo(self):
        """
        Configura os parâmetros iniciais do jogo.
        """
        # Gravidade e vento
        self.gravidade = LVector3(0, 0, -9.8)
        self.vento = LVector3(random.uniform(-1, 1), random.uniform(-1, 1), 0)
        
        # Controle de turnos e pontuação
        self.jogador_atual = 0  # 0 para o primeiro jogador, 1 para o segundo
        self.pontuacao = [0, 0]
        self.max_pontuacao = 3
        
        # Parâmetros de tiro
        self.angulo_horizontal = 45.0
        self.angulo_vertical = 45.0
        self.forca = 50.0
        
        # Lista de projéteis ativos
        self.projeteis = []
        
        # Flag para controlar se o jogador pode atirar
        self.pode_atirar = True

    def criar_gorilas(self):
        """
        Cria os gorilas dos jogadores e os posiciona em prédios aleatórios.
        """
        # Escolhe dois prédios separados para posicionar os gorilas
        predios = self.gerador_cidade.predios
        if len(predios) < 2:
            print("Erro: Não há prédios suficientes para posicionar os gorilas")
            return
            
        # Escolhe dois prédios distantes um do outro
        predios_escolhidos = random.sample(predios, 2)
        
        # Cria o gorila do jogador 1 (vermelho)
        self.gorila1 = Gorilla(self, 'gorila1', (1.0, 0.2, 0.2), predios_escolhidos[0])
        
        # Cria o gorila do jogador 2 (verde)
        self.gorila2 = Gorilla(self, 'gorila2', (0.2, 1.0, 0.2), predios_escolhidos[1])
        
        # Lista de gorilas para facilitar o acesso
        self.gorilas = [self.gorila1, self.gorila2]
        
        # Configura a câmera para o gorila ativo
        self.camera_jogo.focar_gorila(self.gorilas[self.jogador_atual])

    def configurar_tarefas(self):
        """
        Configura as tarefas que serão executadas a cada frame.
        """
        # Tarefa principal de atualização do jogo
        self.taskMgr.add(self.atualizar_jogo, "AtualizarJogo")
        
    def configurar_eventos(self):
        """
        Configura os eventos de entrada (teclado e mouse).
        """
        # Teclas para ajustar ângulo e força
        self.accept("arrow_up", self.aumentar_angulo_vertical)
        self.accept("arrow_down", self.diminuir_angulo_vertical)
        self.accept("arrow_left", self.diminuir_angulo_horizontal)
        self.accept("arrow_right", self.aumentar_angulo_horizontal)
        self.accept("a", self.diminuir_forca)
        self.accept("d", self.aumentar_forca)
        
        # Tecla para atirar
        self.accept("space", self.atirar)
        
        # Teclas para alternar câmeras
        self.accept("c", self.camera_jogo.alternar_modo_camera)
        
        # Tecla para pausar
        self.accept("p", self.alternar_pausa)
        
        # Tecla para sair
        self.accept("escape", self.mostrar_menu_pausa)
        
    def atualizar_jogo(self, task):
        """
        Função principal de atualização do jogo, chamada a cada frame.
        """
        # Obtém o delta time para este frame
        dt = self.taskMgr.globalClock.getDt()
        
        # Só processa se o jogo estiver rodando
        if self.estado_jogo != 'jogando':
            return task.cont
            
        # Atualiza os gorilas
        for gorila in self.gorilas:
            gorila.atualizar(dt)
            
        # Atualiza os projéteis
        self.atualizar_projeteis()
        
        # Atualiza efeitos visuais
        self.efeitos.atualizar()
        
        # Atualiza o sistema de clima
        self.clima.atualizar()
        
        # Atualiza o sistema de destruição
        self.destruicao.atualizar(dt)
        
        # Atualiza a câmera
        self.camera_jogo.atualizar(dt)
        
        # Atualiza a UI
        self.ui.atualizar()
        
        return task.cont
        
    def atualizar_projeteis(self):
        """
        Atualiza todos os projéteis ativos no jogo.
        """
        # Lista de projéteis para remover após a iteração
        para_remover = []
        
        # Atualiza cada projétil
        for projetil in self.projeteis:
            resultado = projetil.atualizar(self.gravidade, self.vento)
            
            # Verifica se o projétil colidiu ou saiu da tela
            if resultado == 'colisao' or resultado == 'fora_limites':
                para_remover.append(projetil)
                
                # Se foi uma colisão, verifica se acertou um gorila
                if resultado == 'colisao':
                    self.verificar_acerto_gorila(projetil)
        
        # Remove os projéteis marcados
        for projetil in para_remover:
            self.projeteis.remove(projetil)
            projetil.remover()
            
        # Se não há projéteis e é necessário trocar de jogador
        if len(self.projeteis) == 0:
            self.pode_atirar = True
            
    def verificar_acerto_gorila(self, projetil):
        """
        Verifica se o projétil acertou um gorila.
        """
        # Gorila alvo (o gorila do jogador oposto)
        indice_alvo = 1 - self.jogador_atual
        gorila_alvo = self.gorilas[indice_alvo]
        
        # Verifica se o projétil acertou o gorila alvo
        if projetil.verificar_colisao_com(gorila_alvo.node):
            # Cria uma explosão no ponto de impacto
            self.efeitos.criar_explosao(projetil.get_pos())
            
            # Toca som de impacto no gorila
            self.som.tocar_som('impacto_gorila', projetil.get_pos())
            
            # Incrementa a pontuação do jogador atual
            self.pontuacao[self.jogador_atual] += 1
            
            # Verifica se o jogador atingiu a pontuação máxima
            if self.pontuacao[self.jogador_atual] >= self.max_pontuacao:
                self.estado_jogo = 'game_over'
                self.mostrar_tela_game_over()
            else:
                # O jogador continua o turno após acertar
                self.novo_turno(manter_jogador=True)
                
            return True
        
        # Cria uma explosão mesmo que não tenha acertado o gorila
        posicao_impacto = projetil.get_pos()
        self.efeitos.criar_explosao(posicao_impacto)
        
        # Verifica se acertou algum prédio
        for predio in self.gerador_cidade.predios:
            if projetil.verificar_colisao_com_predio(predio):
                # Causa danos ao prédio
                self.destruicao.criar_explosao_predio(posicao_impacto, 2.0, predio)
                break
        
        # Troca o jogador se não acertou
        self.novo_turno(manter_jogador=False)
        return False
        
    def atirar(self):
        """
        Lança uma banana na direção determinada pelos ângulos e força.
        """
        if self.estado_jogo != 'jogando' or not self.pode_atirar:
            return
            
        # Impede o jogador de atirar novamente até que o projétil termine
        self.pode_atirar = False
        
        # Obtém o gorila atual
        gorila_atual = self.gorilas[self.jogador_atual]
        
        # Cria uma nova banana na posição do gorila
        banana = Banana(
            self,
            gorila_atual.get_pos(),
            self.angulo_horizontal,
            self.angulo_vertical,
            self.forca
        )
        
        # Adiciona à lista de projéteis
        self.projeteis.append(banana)
        
        # Som de lançamento
        self.som.tocar_som('lancamento', gorila_atual.get_pos())
        
    def novo_turno(self, manter_jogador=False):
        """
        Inicia um novo turno, alterando o jogador atual se necessário.
        """
        # Atualiza o jogador atual se não for para manter o mesmo
        if not manter_jogador:
            self.jogador_atual = 1 - self.jogador_atual
            
        # Gera um novo valor aleatório para o vento, influenciado pelo clima atual
        fator_clima = 1.0
        if hasattr(self, 'clima'):
            if self.clima.clima_atual in ['tempestade', 'chuva']:
                fator_clima = 1.5 + self.clima.intensidade
            elif self.clima.clima_atual == 'neve':
                fator_clima = 0.7
                
        self.vento = LVector3(
            random.uniform(-2, 2) * fator_clima,
            random.uniform(-2, 2) * fator_clima,
            0
        )
        
        # Foca a câmera no gorila atual
        self.camera_jogo.focar_gorila(self.gorilas[self.jogador_atual])
        
        # Atualiza a UI
        self.ui.atualizar_info_jogador()
        
    def aumentar_angulo_horizontal(self):
        self.angulo_horizontal = min(self.angulo_horizontal + 5, 180)
        self.ui.atualizar_info_jogador()
        
    def diminuir_angulo_horizontal(self):
        self.angulo_horizontal = max(self.angulo_horizontal - 5, 0)
        self.ui.atualizar_info_jogador()
        
    def aumentar_angulo_vertical(self):
        self.angulo_vertical = min(self.angulo_vertical + 5, 90)
        self.ui.atualizar_info_jogador()
        
    def diminuir_angulo_vertical(self):
        self.angulo_vertical = max(self.angulo_vertical - 5, 0)
        self.ui.atualizar_info_jogador()
        
    def aumentar_forca(self):
        self.forca = min(self.forca + 5, 100)
        self.ui.atualizar_info_jogador()
        
    def diminuir_forca(self):
        self.forca = max(self.forca - 5, 10)
        self.ui.atualizar_info_jogador()
        
    def alternar_pausa(self):
        """
        Alterna o estado de pausa do jogo.
        """
        if self.estado_jogo == 'jogando':
            self.estado_jogo = 'pausado'
            self.mostrar_menu_pausa()
        elif self.estado_jogo == 'pausado':
            self.estado_jogo = 'jogando'
            self.esconder_menu_pausa()
            
    def mostrar_menu_principal(self):
        """
        Mostra o menu principal do jogo.
        """
        self.estado_jogo = 'menu'
        self.ui.mostrar_menu_principal()
        
        # Toca música do menu
        if hasattr(self, 'som'):
            self.som.tocar_musica('menu')
        
    def mostrar_menu_pausa(self):
        """
        Mostra o menu de pausa.
        """
        self.estado_jogo = 'pausado'
        self.ui.mostrar_menu_pausa()
        
    def esconder_menu_pausa(self):
        """
        Esconde o menu de pausa.
        """
        self.ui.esconder_menu_pausa()
        
    def mostrar_tela_game_over(self):
        """
        Mostra a tela de fim de jogo.
        """
        self.estado_jogo = 'game_over'
        self.ui.mostrar_tela_game_over()
        
        # Toca música de fim de jogo
        if hasattr(self, 'som'):
            self.som.tocar_musica('game_over')
            
            # Toca som de vitória
            self.som.tocar_som('vitoria')
        
    def iniciar_jogo(self):
        """
        Inicia um novo jogo.
        """
        # Reinicia todos os parâmetros do jogo
        self.pontuacao = [0, 0]
        self.jogador_atual = 0
        self.vento = LVector3(random.uniform(-2, 2), random.uniform(-2, 2), 0)
        
        # Regenera a cidade
        self.gerador_cidade.limpar_cidade()
        self.cidade = self.gerador_cidade.gerar_cidade(7, 7)
        
        # Recria os gorilas
        self.criar_gorilas()
        
        # Limpa todos os projéteis
        for projetil in self.projeteis:
            projetil.remover()
        self.projeteis = []
        
        # Limpa o sistema de destruição
        if hasattr(self, 'destruicao'):
            self.destruicao.limpar()
        
        # Define um clima aleatório
        if hasattr(self, 'clima'):
            clima_info = self.clima.clima_aleatorio()
            print(f"Clima atual: {clima_info[0]}, Intensidade: {clima_info[1]:.1f}")
        
        # Configura a câmera inicial
        self.camera_jogo.focar_gorila(self.gorilas[self.jogador_atual])
        
        # Configura o estado do jogo
        self.estado_jogo = 'jogando'
        self.pode_atirar = True
        
        # Atualiza a UI
        self.ui.atualizar_info_jogador()
        
        # Esconde todos os menus
        self.ui.esconder_todos_menus()
        
        # Inicia a música do jogo
        if hasattr(self, 'som'):
            self.som.tocar_musica('jogo')
        
    def sair_jogo(self):
        """
        Sai do jogo e fecha a aplicação.
        """
        # Limpa recursos antes de sair
        if hasattr(self, 'som'):
            self.som.limpar()
            
        if hasattr(self, 'clima'):
            self.clima.limpar()
            
        if hasattr(self, 'destruicao'):
            self.destruicao.limpar()
            
        sys.exit()

# Função principal para iniciar o jogo
def main():
    """
    Função principal que inicia o jogo.
    """
    jogo = Gorillas3DWar()
    jogo.run()

if __name__ == "__main__":
    main()
