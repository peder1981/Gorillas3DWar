#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gorillas 3D War - Jogo inspirado no clássico Gorillas do QBasic
Versão 3D com efeitos avançados, clima dinâmico e sistema de destruição
"""

import sys
import random
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData

from src.game import Game

# Configurações iniciais para o Panda3D
loadPrcFileData("", """
    window-title Gorillas 3D War
    fullscreen 0
    win-size 1280 720
    sync-video 0
    show-frame-rate-meter 1
    texture-compression 1
    model-cache-dir cache
    audio-buffering-seconds 0.5
    audio-library-name p3openal_audio
""")

def main():
    """
    Função principal que inicializa e executa o jogo.
    """
    # Inicia o jogo
    print("Iniciando Gorillas 3D War...")
    game = Game()
    game.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nJogo encerrado pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"Erro durante a execução do jogo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
