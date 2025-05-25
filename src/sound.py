#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gorillas 3D War - Módulo de gerenciamento de sons
"""
from direct.showbase import Audio3DManager
from panda3d.core import AudioSound, Vec3, NodePath

class SoundManager:
    """
    Gerenciador de sons para o jogo, incluindo efeitos sonoros e música.
    """
    def __init__(self, game):
        """
        Inicializa o gerenciador de sons.
        
        Args:
            game: Referência ao jogo principal.
        """
        self.game = game
        
        # Inicializa o gerenciador de áudio 3D
        self.audio3d = Audio3DManager.Audio3DManager(
            game.sfxManagerList[0], game.camera)
        
        # Dicionário para armazenar sons
        self.sons = {}
        
        # Dicionário para armazenar músicas
        self.musicas = {}
        
        # Volume padrão
        self.volume_efeitos = 0.7
        self.volume_musica = 0.5
        
        # Carrega os sons
        self.carregar_sons()
        
    def carregar_sons(self):
        """
        Carrega todos os efeitos sonoros e músicas utilizados no jogo.
        """
        # Lista de efeitos sonoros a serem carregados
        efeitos = {
            'lancamento': 'sounds/launch.wav',
            'explosao': 'sounds/explosion.wav',
            'impacto_predio': 'sounds/building_hit.wav',
            'impacto_gorila': 'sounds/gorilla_hit.wav',
            'vitoria': 'sounds/victory.wav',
            'selecao_menu': 'sounds/menu_select.wav',
            'confirma_menu': 'sounds/menu_confirm.wav',
            'vento': 'sounds/wind.wav',
            'chuva': 'sounds/rain.wav',
            'trovao': 'sounds/thunder.wav'
        }
        
        # Lista de músicas a serem carregadas
        musicas = {
            'menu': 'sounds/menu_music.wav',
            'jogo': 'sounds/game_music.wav',
            'game_over': 'sounds/game_over_music.wav'
        }
        
        # Carrega os efeitos sonoros
        for nome, caminho in efeitos.items():
            try:
                self.sons[nome] = self.carregar_som(caminho, is_3d=True)
                if self.sons[nome]:
                    self.sons[nome].setVolume(self.volume_efeitos)
            except Exception as e:
                print(f"Aviso: Não foi possível carregar o som '{nome}' de '{caminho}': {e}")
                self.sons[nome] = None
        
        # Carrega as músicas
        for nome, caminho in musicas.items():
            try:
                self.musicas[nome] = self.carregar_som(caminho, is_3d=False, loop=True)
                if self.musicas[nome]:
                    self.musicas[nome].setVolume(self.volume_musica)
            except Exception as e:
                print(f"Aviso: Não foi possível carregar a música '{nome}' de '{caminho}': {e}")
                self.musicas[nome] = None
    
    def carregar_som(self, caminho, is_3d=False, loop=False):
        """
        Carrega um arquivo de som.
        
        Args:
            caminho: Caminho para o arquivo de som.
            3d: Se True, carrega como som 3D. Se False, carrega como som 2D.
            loop: Se True, configura o som para tocar em loop.
            
        Returns:
            Referência para o som carregado ou None se falhar.
        """
        try:
            if is_3d:
                    som = self.audio3d.loadSfx(caminho)
            else:
                som = self.game.loader.loadSfx(caminho)
                
            if loop:
                som.setLoop(True)
                
            return som
        except:
            print(f"Erro ao carregar o som: {caminho}")
            return None
    
    def tocar_som(self, nome, posicao=None, volume=None):
        """
        Toca um efeito sonoro.
        
        Args:
            nome: Nome do som a ser tocado.
            posicao: Posição 3D do som (para sons 3D).
            volume: Volume do som (opcional).
        """
        if nome not in self.sons or self.sons[nome] is None:
            return
            
        som = self.sons[nome]
        
        # Define o volume
        if volume is not None:
            som.setVolume(volume)
        else:
            som.setVolume(self.volume_efeitos)
            
        # Define a posição 3D
        if posicao is not None:
            # Precisamos criar um NodePath para associar o som, já que attachSoundToObject
            # espera um NodePath e não apenas uma posição Vec3
            temp_node = NodePath("sound_node")
            
            # Converte para Vec3 se for uma tupla
            if isinstance(posicao, tuple) and len(posicao) == 3:
                pos_vec = Vec3(posicao[0], posicao[1], posicao[2])
                temp_node.setPos(pos_vec)
            elif isinstance(posicao, Vec3):
                # Se já é um Vec3, use-o diretamente
                temp_node.setPos(posicao)
            elif isinstance(posicao, NodePath):
                # Se já é um NodePath, use-o diretamente
                temp_node = posicao
            
            # Associa o som ao node path temporário
            self.audio3d.attachSoundToObject(som, temp_node)
            
        # Toca o som se não estiver tocando
        if not som.status() == AudioSound.PLAYING:
            som.play()
    
    def tocar_musica(self, nome):
        """
        Toca uma música.
        
        Args:
            nome: Nome da música a ser tocada.
        """
        # Para todas as músicas atuais
        for musica in self.musicas.values():
            if musica and musica.status() == AudioSound.PLAYING:
                musica.stop()
                
        # Toca a nova música
        if nome in self.musicas and self.musicas[nome]:
            self.musicas[nome].setVolume(self.volume_musica)
            self.musicas[nome].play()
    
    def parar_musica(self):
        """
        Para todas as músicas.
        """
        for musica in self.musicas.values():
            if musica:
                musica.stop()
    
    def parar_som(self, nome):
        """
        Para um efeito sonoro específico.
        
        Args:
            nome: Nome do som a ser parado.
        """
        if nome in self.sons and self.sons[nome]:
            self.sons[nome].stop()
    
    def definir_volume_efeitos(self, volume):
        """
        Define o volume dos efeitos sonoros.
        
        Args:
            volume: Valor do volume (0.0 a 1.0).
        """
        self.volume_efeitos = max(0.0, min(1.0, volume))
        
        # Atualiza o volume de todos os efeitos
        for som in self.sons.values():
            if som:
                som.setVolume(self.volume_efeitos)
    
    def definir_volume_musica(self, volume):
        """
        Define o volume das músicas.
        
        Args:
            volume: Valor do volume (0.0 a 1.0).
        """
        self.volume_musica = max(0.0, min(1.0, volume))
        
        # Atualiza o volume de todas as músicas
        for musica in self.musicas.values():
            if musica:
                musica.setVolume(self.volume_musica)
    
    def iniciar_som_ambiente(self, tipo):
        """
        Inicia um som ambiente contínuo.
        
        Args:
            tipo: Tipo de som ambiente ('vento', 'chuva', etc).
        """
        if tipo in self.sons and self.sons[tipo]:
            som = self.sons[tipo]
            som.setLoop(True)
            
            if not som.status() == AudioSound.PLAYING:
                som.play()
    
    def parar_som_ambiente(self, tipo):
        """
        Para um som ambiente.
        
        Args:
            tipo: Tipo de som ambiente ('vento', 'chuva', etc).
        """
        if tipo in self.sons and self.sons[tipo]:
            som = self.sons[tipo]
            som.setLoop(False)
            som.stop()
    
    def limpar(self):
        """
        Limpa todos os sons carregados.
        """
        # Para todos os sons
        for som in self.sons.values():
            if som:
                som.stop()
        
        # Para todas as músicas
        for musica in self.musicas.values():
            if musica:
                musica.stop()
                
        # Limpa dicionários
        self.sons.clear()
        self.musicas.clear()
