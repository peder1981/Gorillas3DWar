#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gorillas 3D War - Módulo para interface do usuário
"""
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectFrame, DirectButton, DirectSlider, DirectLabel
from direct.gui.DirectGui import DGG
from panda3d.core import TextNode, TransparencyAttrib
import math

class GameUI:
    """
    Classe para gerenciar a interface do usuário do jogo.
    """
    def __init__(self, game):
        """
        Inicializa a interface do usuário.
        
        Args:
            game: Referência ao jogo principal.
        """
        self.game = game
        
        # Fontes
        self.fonte_pequena = self.game.loader.loadFont("cmss12")
        self.fonte_media = self.game.loader.loadFont("cmss12")
        self.fonte_grande = self.game.loader.loadFont("cmss12")
        
        # Ajusta as fontes - não precisamos verificar se estão vazias,
        # pois o Panda3D lida com isso automaticamente
        try:
            self.fonte_pequena.setPixelsPerUnit(60)
            self.fonte_media.setPixelsPerUnit(80)
            self.fonte_grande.setPixelsPerUnit(120)
        except Exception as e:
            print(f"Aviso: Não foi possível ajustar as fontes: {e}")
            # Continua mesmo se não puder ajustar as fontes
        
        # HUD do jogo
        self.criar_hud()
        
        # Menus do jogo
        self.menu_principal = None
        self.menu_pausa = None
        self.tela_game_over = None
        
        # Cria os menus
        self.criar_menu_principal()
        self.criar_menu_pausa()
        self.criar_tela_game_over()
        
        # Esconde todos os menus inicialmente
        self.esconder_todos_menus()
        
    def criar_hud(self):
        """
        Cria o HUD (Heads-Up Display) do jogo.
        """
        # Frame principal do HUD
        self.hud_frame = DirectFrame(
            frameColor=(0, 0, 0, 0.5),
            frameSize=(-1, 1, -0.1, 0.1),
            pos=(0, 0, -0.9)
        )
        
        # Informações do jogador atual
        self.jogador_texto = OnscreenText(
            text="Jogador 1",
            pos=(-0.95, -0.95),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=True,
            font=self.fonte_media
        )
        
        # Ângulos e força
        self.angulo_h_texto = OnscreenText(
            text="Ângulo H: 45°",
            pos=(-0.5, -0.95),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=True,
            font=self.fonte_pequena
        )
        
        self.angulo_v_texto = OnscreenText(
            text="Ângulo V: 45°",
            pos=(-0.5, -0.85),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=True,
            font=self.fonte_pequena
        )
        
        self.forca_texto = OnscreenText(
            text="Força: 50",
            pos=(-0.1, -0.95),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=True,
            font=self.fonte_pequena
        )
        
        # Informações do vento
        self.vento_texto = OnscreenText(
            text="Vento: →",
            pos=(0.3, -0.95),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=True,
            font=self.fonte_pequena
        )
        
        # Pontuação
        self.pontuacao_texto = OnscreenText(
            text="Placar: 0 - 0",
            pos=(0.8, -0.95),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=TextNode.ARight,
            mayChange=True,
            font=self.fonte_pequena
        )
        
        # Instruções
        self.instrucoes_texto = OnscreenText(
            text="← → = Ângulo H  |  ↑ ↓ = Ângulo V  |  A D = Força  |  Espaço = Lançar  |  C = Câmera  |  P = Pausa",
            pos=(0, -0.85),
            scale=0.04,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter,
            mayChange=True,
            font=self.fonte_pequena
        )
        
    def criar_menu_principal(self):
        """
        Cria o menu principal do jogo.
        """
        # Frame principal do menu
        self.menu_principal = DirectFrame(
            frameColor=(0, 0, 0, 0.7),
            frameSize=(-1, 1, -1, 1),
            pos=(0, 0, 0)
        )
        
        # Título do jogo
        titulo = OnscreenText(
            text="GORILLAS 3D WAR",
            pos=(0, 0.6),
            scale=0.15,
            fg=(1, 0.8, 0, 1),
            shadow=(0, 0, 0, 1),
            align=TextNode.ACenter,
            mayChange=False,
            parent=self.menu_principal,
            font=self.fonte_grande
        )
        
        # Botões do menu
        botao_jogar = DirectButton(
            text="Jogar",
            scale=0.1,
            command=self.game.iniciar_jogo,
            frameColor=(0.2, 0.6, 0.2, 0.8),
            relief=DGG.FLAT,
            text_fg=(1, 1, 1, 1),
            text_pos=(0, -0.04),
            text_scale=0.8,
            frameSize=(-2, 2, -0.5, 0.5),
            pos=(0, 0, 0.2),
            parent=self.menu_principal
        )
        
        botao_sair = DirectButton(
            text="Sair",
            scale=0.1,
            command=self.game.sair_jogo,
            frameColor=(0.6, 0.2, 0.2, 0.8),
            relief=DGG.FLAT,
            text_fg=(1, 1, 1, 1),
            text_pos=(0, -0.04),
            text_scale=0.8,
            frameSize=(-2, 2, -0.5, 0.5),
            pos=(0, 0, -0.1),
            parent=self.menu_principal
        )
        
        # Versão do jogo
        versao = OnscreenText(
            text="v1.0",
            pos=(0.95, -0.95),
            scale=0.05,
            fg=(1, 1, 1, 0.7),
            align=TextNode.ARight,
            mayChange=False,
            parent=self.menu_principal
        )
        
    def criar_menu_pausa(self):
        """
        Cria o menu de pausa do jogo.
        """
        # Frame principal do menu de pausa
        self.menu_pausa = DirectFrame(
            frameColor=(0, 0, 0, 0.7),
            frameSize=(-0.5, 0.5, -0.6, 0.6),
            pos=(0, 0, 0)
        )
        
        # Título do menu
        titulo = OnscreenText(
            text="PAUSA",
            pos=(0, 0.4),
            scale=0.1,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter,
            mayChange=False,
            parent=self.menu_pausa
        )
        
        # Botões do menu
        botao_continuar = DirectButton(
            text="Continuar",
            scale=0.07,
            command=self.game.alternar_pausa,
            frameColor=(0.2, 0.6, 0.2, 0.8),
            relief=DGG.FLAT,
            text_fg=(1, 1, 1, 1),
            text_pos=(0, -0.04),
            text_scale=0.8,
            frameSize=(-2, 2, -0.5, 0.5),
            pos=(0, 0, 0.2),
            parent=self.menu_pausa
        )
        
        botao_reiniciar = DirectButton(
            text="Reiniciar",
            scale=0.07,
            command=self.game.iniciar_jogo,
            frameColor=(0.4, 0.4, 0.6, 0.8),
            relief=DGG.FLAT,
            text_fg=(1, 1, 1, 1),
            text_pos=(0, -0.04),
            text_scale=0.8,
            frameSize=(-2, 2, -0.5, 0.5),
            pos=(0, 0, 0.0),
            parent=self.menu_pausa
        )
        
        botao_menu = DirectButton(
            text="Menu Principal",
            scale=0.07,
            command=self.game.mostrar_menu_principal,
            frameColor=(0.4, 0.4, 0.4, 0.8),
            relief=DGG.FLAT,
            text_fg=(1, 1, 1, 1),
            text_pos=(0, -0.04),
            text_scale=0.8,
            frameSize=(-2, 2, -0.5, 0.5),
            pos=(0, 0, -0.2),
            parent=self.menu_pausa
        )
        
        botao_sair = DirectButton(
            text="Sair do Jogo",
            scale=0.07,
            command=self.game.sair_jogo,
            frameColor=(0.6, 0.2, 0.2, 0.8),
            relief=DGG.FLAT,
            text_fg=(1, 1, 1, 1),
            text_pos=(0, -0.04),
            text_scale=0.8,
            frameSize=(-2, 2, -0.5, 0.5),
            pos=(0, 0, -0.4),
            parent=self.menu_pausa
        )
        
    def criar_tela_game_over(self):
        """
        Cria a tela de game over.
        """
        # Frame principal da tela de game over
        self.tela_game_over = DirectFrame(
            frameColor=(0, 0, 0, 0.7),
            frameSize=(-0.8, 0.8, -0.6, 0.6),
            pos=(0, 0, 0)
        )
        
        # Título
        self.game_over_titulo = OnscreenText(
            text="FIM DE JOGO",
            pos=(0, 0.4),
            scale=0.12,
            fg=(1, 0.8, 0, 1),
            align=TextNode.ACenter,
            mayChange=True,
            parent=self.tela_game_over
        )
        
        # Texto do vencedor
        self.vencedor_texto = OnscreenText(
            text="Jogador 1 Venceu!",
            pos=(0, 0.2),
            scale=0.08,
            fg=(1, 0.2, 0.2, 1),
            align=TextNode.ACenter,
            mayChange=True,
            parent=self.tela_game_over
        )
        
        # Placar
        self.placar_texto = OnscreenText(
            text="Placar: 3 - 0",
            pos=(0, 0.0),
            scale=0.07,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter,
            mayChange=True,
            parent=self.tela_game_over
        )
        
        # Botões
        botao_jogar_novamente = DirectButton(
            text="Jogar Novamente",
            scale=0.07,
            command=self.game.iniciar_jogo,
            frameColor=(0.2, 0.6, 0.2, 0.8),
            relief=DGG.FLAT,
            text_fg=(1, 1, 1, 1),
            text_pos=(0, -0.04),
            text_scale=0.8,
            frameSize=(-2, 2, -0.5, 0.5),
            pos=(0, 0, -0.2),
            parent=self.tela_game_over
        )
        
        botao_menu = DirectButton(
            text="Menu Principal",
            scale=0.07,
            command=self.game.mostrar_menu_principal,
            frameColor=(0.4, 0.4, 0.4, 0.8),
            relief=DGG.FLAT,
            text_fg=(1, 1, 1, 1),
            text_pos=(0, -0.04),
            text_scale=0.8,
            frameSize=(-2, 2, -0.5, 0.5),
            pos=(0, 0, -0.4),
            parent=self.tela_game_over
        )
        
    def atualizar(self):
        """
        Atualiza os elementos da interface com as informações atuais do jogo.
        """
        # Só atualiza se estiver no estado jogando
        if self.game.estado_jogo != 'jogando':
            return
            
        # Atualiza informações do jogador
        self.atualizar_info_jogador()
        
        # Atualiza informações do vento
        self.atualizar_info_vento()
        
        # Atualiza pontuação
        self.pontuacao_texto.setText(f"Placar: {self.game.pontuacao[0]} - {self.game.pontuacao[1]}")
        
    def atualizar_info_jogador(self):
        """
        Atualiza as informações do jogador atual.
        """
        # Jogador atual
        jogador_texto = f"Jogador {self.game.jogador_atual + 1}"
        cor = (1, 0.2, 0.2, 1) if self.game.jogador_atual == 0 else (0.2, 1, 0.2, 1)
        self.jogador_texto.setText(jogador_texto)
        self.jogador_texto.setFg(cor)
        
        # Ângulos e força
        self.angulo_h_texto.setText(f"Ângulo H: {int(self.game.angulo_horizontal)}°")
        self.angulo_v_texto.setText(f"Ângulo V: {int(self.game.angulo_vertical)}°")
        self.forca_texto.setText(f"Força: {int(self.game.forca)}")
        
    def atualizar_info_vento(self):
        """
        Atualiza as informações de vento.
        """
        # Converte o vetor de vento para texto com setas
        vento_x = self.game.vento.getX()
        vento_y = self.game.vento.getY()
        
        # Calcula magnitude e direção
        magnitude = math.sqrt(vento_x ** 2 + vento_y ** 2)
        
        # Determina a seta baseada na direção do vento
        if abs(vento_x) > abs(vento_y):
            # Predominantemente horizontal
            if vento_x > 0:
                direcao = "→"
            else:
                direcao = "←"
        else:
            # Predominantemente vertical
            if vento_y > 0:
                direcao = "↑"
            else:
                direcao = "↓"
        
        # Textos de intensidade
        intensidade = ""
        if magnitude < 0.5:
            intensidade = "Fraco"
        elif magnitude < 1.5:
            intensidade = "Médio"
        else:
            intensidade = "Forte"
            
        self.vento_texto.setText(f"Vento: {direcao} {intensidade}")
        
    def mostrar_menu_principal(self):
        """
        Mostra o menu principal.
        """
        self.esconder_todos_menus()
        self.menu_principal.show()
        
    def mostrar_menu_pausa(self):
        """
        Mostra o menu de pausa.
        """
        self.esconder_todos_menus()
        self.menu_pausa.show()
        
    def mostrar_tela_game_over(self):
        """
        Mostra a tela de game over.
        """
        # Determina o vencedor
        if self.game.pontuacao[0] > self.game.pontuacao[1]:
            vencedor = "Jogador 1"
            cor = (1, 0.2, 0.2, 1)
        else:
            vencedor = "Jogador 2"
            cor = (0.2, 1, 0.2, 1)
            
        # Atualiza os textos
        self.vencedor_texto.setText(f"{vencedor} Venceu!")
        self.vencedor_texto.setFg(cor)
        self.placar_texto.setText(f"Placar: {self.game.pontuacao[0]} - {self.game.pontuacao[1]}")
        
        # Mostra a tela
        self.esconder_todos_menus()
        self.tela_game_over.show()
        
    def esconder_todos_menus(self):
        """
        Esconde todos os menus.
        """
        if self.menu_principal:
            self.menu_principal.hide()
        if self.menu_pausa:
            self.menu_pausa.hide()
        if self.tela_game_over:
            self.tela_game_over.hide()
            
    def esconder_menu_pausa(self):
        """
        Esconde apenas o menu de pausa.
        """
        if self.menu_pausa:
            self.menu_pausa.hide()
