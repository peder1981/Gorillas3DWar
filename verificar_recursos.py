#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar e criar recursos básicos para o Gorillas 3D War
"""
import os
import shutil
import random
from pathlib import Path

class VerificadorRecursos:
    """Classe para verificar e criar recursos básicos para o jogo"""
    
    def __init__(self):
        """Inicializa o verificador de recursos"""
        self.diretorio_base = os.path.dirname(os.path.abspath(__file__))
        self.diretorio_modelos = os.path.join(self.diretorio_base, "models")
        self.diretorio_texturas = os.path.join(self.diretorio_base, "textures")
        self.diretorio_sons = os.path.join(self.diretorio_base, "sounds")
        self.diretorio_assets = os.path.join(self.diretorio_base, "assets")
        
        # Cria diretórios base se não existirem
        os.makedirs(self.diretorio_modelos, exist_ok=True)
        os.makedirs(self.diretorio_texturas, exist_ok=True)
        os.makedirs(self.diretorio_sons, exist_ok=True)
        os.makedirs(self.diretorio_assets, exist_ok=True)
        
        # Subdiretórios para modelos
        os.makedirs(os.path.join(self.diretorio_modelos, "misc"), exist_ok=True)
        os.makedirs(os.path.join(self.diretorio_modelos, "buildings"), exist_ok=True)
        os.makedirs(os.path.join(self.diretorio_modelos, "characters"), exist_ok=True)
        
    def verificar_e_criar_recursos(self):
        """Verifica e cria recursos básicos para o jogo"""
        print("Verificando recursos básicos do jogo...")
        
        # Verifica e cria modelos básicos
        self._verificar_e_criar_modelos()
        
        # Verifica e cria texturas básicas
        self._verificar_e_criar_texturas()
        
        # Verifica e cria sons básicos
        self._verificar_e_criar_sons()
        
        print("Verificação de recursos concluída!")
        
    def _verificar_e_criar_modelos(self):
        """Verifica e cria modelos básicos"""
        print("Verificando modelos básicos...")
        
        # Lista de modelos básicos para verificar
        modelos_basicos = [
            ("misc/plane", self._criar_modelo_plano),
            ("misc/sphere", self._criar_modelo_esfera),
            ("misc/box", self._criar_modelo_caixa),
            ("characters/gorilla", self._criar_modelo_gorila),
        ]
        
        # Verifica e cria cada modelo
        for nome_modelo, funcao_criar in modelos_basicos:
            # Garante que a pasta existe
            pasta_modelo = os.path.dirname(os.path.join(self.diretorio_modelos, nome_modelo))
            os.makedirs(pasta_modelo, exist_ok=True)
            
            caminho_modelo = os.path.join(self.diretorio_modelos, f"{nome_modelo}.egg")
            if not os.path.exists(caminho_modelo):
                print(f"Criando modelo básico: {nome_modelo}")
                funcao_criar(caminho_modelo)
            else:
                print(f"Modelo existente: {nome_modelo}")
                
    def _criar_modelo_plano(self, caminho):
        """Cria um modelo de plano básico no formato EGG"""
        with open(caminho, 'w') as f:
            f.write("""<CoordinateSystem> { Z-up }

<Group> Plane {
  <VertexPool> PlaneVerts {
    <Vertex> 1 {
      -1 -1 0
      <Normal> { 0 0 1 }
    }
    <Vertex> 2 {
      1 -1 0
      <Normal> { 0 0 1 }
    }
    <Vertex> 3 {
      1 1 0
      <Normal> { 0 0 1 }
    }
    <Vertex> 4 {
      -1 1 0
      <Normal> { 0 0 1 }
    }
  }
  <Polygon> {
    <Normal> { 0 0 1 }
    <VertexRef> { 1 2 3 4 <Ref> { PlaneVerts } }
  }
}""")
            
    def _criar_modelo_esfera(self, caminho):
        """Cria um modelo de esfera básico no formato EGG"""
        with open(caminho, 'w') as f:
            f.write("""<CoordinateSystem> { Z-up }

<Group> Sphere {
  <VertexPool> SphereVerts {
    <Vertex> 1 {
      0 0 1
      <Normal> { 0 0 1 }
    }
    <Vertex> 2 {
      0.707 0 0.707
      <Normal> { 0.707 0 0.707 }
    }
    <Vertex> 3 {
      0 0.707 0.707
      <Normal> { 0 0.707 0.707 }
    }
    <Vertex> 4 {
      -0.707 0 0.707
      <Normal> { -0.707 0 0.707 }
    }
    <Vertex> 5 {
      0 -0.707 0.707
      <Normal> { 0 -0.707 0.707 }
    }
    <Vertex> 6 {
      0 0 -1
      <Normal> { 0 0 -1 }
    }
    <Vertex> 7 {
      0.707 0 -0.707
      <Normal> { 0.707 0 -0.707 }
    }
    <Vertex> 8 {
      0 0.707 -0.707
      <Normal> { 0 0.707 -0.707 }
    }
    <Vertex> 9 {
      -0.707 0 -0.707
      <Normal> { -0.707 0 -0.707 }
    }
    <Vertex> 10 {
      0 -0.707 -0.707
      <Normal> { 0 -0.707 -0.707 }
    }
  }
  <Polygon> {
    <VertexRef> { 1 2 3 <Ref> { SphereVerts } }
  }
  <Polygon> {
    <VertexRef> { 1 3 4 <Ref> { SphereVerts } }
  }
  <Polygon> {
    <VertexRef> { 1 4 5 <Ref> { SphereVerts } }
  }
  <Polygon> {
    <VertexRef> { 1 5 2 <Ref> { SphereVerts } }
  }
  <Polygon> {
    <VertexRef> { 6 8 7 <Ref> { SphereVerts } }
  }
  <Polygon> {
    <VertexRef> { 6 9 8 <Ref> { SphereVerts } }
  }
  <Polygon> {
    <VertexRef> { 6 10 9 <Ref> { SphereVerts } }
  }
  <Polygon> {
    <VertexRef> { 6 7 10 <Ref> { SphereVerts } }
  }
  <Polygon> {
    <VertexRef> { 2 3 8 7 <Ref> { SphereVerts } }
  }
  <Polygon> {
    <VertexRef> { 3 4 9 8 <Ref> { SphereVerts } }
  }
  <Polygon> {
    <VertexRef> { 4 5 10 9 <Ref> { SphereVerts } }
  }
  <Polygon> {
    <VertexRef> { 5 2 7 10 <Ref> { SphereVerts } }
  }
}""")
            
    def _criar_modelo_caixa(self, caminho):
        """Cria um modelo de caixa básico no formato EGG"""
        with open(caminho, 'w') as f:
            f.write("""<CoordinateSystem> { Z-up }

<Group> Box {
  <VertexPool> BoxVerts {
    <Vertex> 1 {
      -1 -1 -1
      <Normal> { -1 0 0 }
    }
    <Vertex> 2 {
      -1 1 -1
      <Normal> { -1 0 0 }
    }
    <Vertex> 3 {
      -1 1 1
      <Normal> { -1 0 0 }
    }
    <Vertex> 4 {
      -1 -1 1
      <Normal> { -1 0 0 }
    }
    <Vertex> 5 {
      1 -1 -1
      <Normal> { 1 0 0 }
    }
    <Vertex> 6 {
      1 1 -1
      <Normal> { 1 0 0 }
    }
    <Vertex> 7 {
      1 1 1
      <Normal> { 1 0 0 }
    }
    <Vertex> 8 {
      1 -1 1
      <Normal> { 1 0 0 }
    }
    <Vertex> 9 {
      -1 -1 -1
      <Normal> { 0 -1 0 }
    }
    <Vertex> 10 {
      1 -1 -1
      <Normal> { 0 -1 0 }
    }
    <Vertex> 11 {
      1 -1 1
      <Normal> { 0 -1 0 }
    }
    <Vertex> 12 {
      -1 -1 1
      <Normal> { 0 -1 0 }
    }
    <Vertex> 13 {
      -1 1 -1
      <Normal> { 0 1 0 }
    }
    <Vertex> 14 {
      1 1 -1
      <Normal> { 0 1 0 }
    }
    <Vertex> 15 {
      1 1 1
      <Normal> { 0 1 0 }
    }
    <Vertex> 16 {
      -1 1 1
      <Normal> { 0 1 0 }
    }
    <Vertex> 17 {
      -1 -1 -1
      <Normal> { 0 0 -1 }
    }
    <Vertex> 18 {
      1 -1 -1
      <Normal> { 0 0 -1 }
    }
    <Vertex> 19 {
      1 1 -1
      <Normal> { 0 0 -1 }
    }
    <Vertex> 20 {
      -1 1 -1
      <Normal> { 0 0 -1 }
    }
    <Vertex> 21 {
      -1 -1 1
      <Normal> { 0 0 1 }
    }
    <Vertex> 22 {
      1 -1 1
      <Normal> { 0 0 1 }
    }
    <Vertex> 23 {
      1 1 1
      <Normal> { 0 0 1 }
    }
    <Vertex> 24 {
      -1 1 1
      <Normal> { 0 0 1 }
    }
  }
  <Polygon> {
    <VertexRef> { 1 2 3 4 <Ref> { BoxVerts } }
  }
  <Polygon> {
    <VertexRef> { 8 7 6 5 <Ref> { BoxVerts } }
  }
  <Polygon> {
    <VertexRef> { 9 10 11 12 <Ref> { BoxVerts } }
  }
  <Polygon> {
    <VertexRef> { 16 15 14 13 <Ref> { BoxVerts } }
  }
  <Polygon> {
    <VertexRef> { 17 18 19 20 <Ref> { BoxVerts } }
  }
  <Polygon> {
    <VertexRef> { 24 23 22 21 <Ref> { BoxVerts } }
  }
}""")
            
    def _criar_modelo_gorila(self, caminho):
        """Cria um modelo de gorila básico no formato EGG"""
        with open(caminho, 'w') as f:
            f.write("""<CoordinateSystem> { Z-up }

<Group> Gorilla {
  <VertexPool> GorillaVerts {
    # Corpo do gorila (tronco)
    <Vertex> 1 {
      0 0 0
      <Normal> { 0 0 1 }
    }
    <Vertex> 2 {
      0.7 0 0
      <Normal> { 0 0 1 }
    }
    <Vertex> 3 {
      0.7 0 1.4
      <Normal> { 0 0 1 }
    }
    <Vertex> 4 {
      0 0 1.4
      <Normal> { 0 0 1 }
    }
    
    # Cabeça (esfera simples)
    <Vertex> 5 {
      0.35 0 1.6
      <Normal> { 0 0 1 }
    }
    <Vertex> 6 {
      0.6 0 1.6
      <Normal> { 1 0 0 }
    }
    <Vertex> 7 {
      0.35 0 1.85
      <Normal> { 0 0 1 }
    }
    <Vertex> 8 {
      0.1 0 1.6
      <Normal> { -1 0 0 }
    }
    
    # Braço direito
    <Vertex> 9 {
      0.7 0 1.0
      <Normal> { 1 0 0 }
    }
    <Vertex> 10 {
      1.1 0 1.0
      <Normal> { 1 0 0 }
    }
    <Vertex> 11 {
      1.1 0 0.6
      <Normal> { 1 0 0 }
    }
    <Vertex> 12 {
      0.7 0 0.6
      <Normal> { 1 0 0 }
    }
    
    # Braço esquerdo
    <Vertex> 13 {
      0 0 1.0
      <Normal> { -1 0 0 }
    }
    <Vertex> 14 {
      -0.4 0 1.0
      <Normal> { -1 0 0 }
    }
    <Vertex> 15 {
      -0.4 0 0.6
      <Normal> { -1 0 0 }
    }
    <Vertex> 16 {
      0 0 0.6
      <Normal> { -1 0 0 }
    }
  }
  
  # Tronco
  <Polygon> {
    <VertexRef> { 1 2 3 4 <Ref> { GorillaVerts } }
  }
  
  # Cabeça (triângulos)
  <Polygon> {
    <VertexRef> { 5 6 7 <Ref> { GorillaVerts } }
  }
  <Polygon> {
    <VertexRef> { 5 7 8 <Ref> { GorillaVerts } }
  }
  <Polygon> {
    <VertexRef> { 5 8 6 <Ref> { GorillaVerts } }
  }
  
  # Braço direito
  <Polygon> {
    <VertexRef> { 9 10 11 12 <Ref> { GorillaVerts } }
  }
  
  # Braço esquerdo
  <Polygon> {
    <VertexRef> { 13 14 15 16 <Ref> { GorillaVerts } }
  }
}""")
            
    def _verificar_e_criar_texturas(self):
        """Verifica e cria texturas básicas"""
        print("Verificando texturas básicas...")
        
        # Lista de texturas básicas
        texturas_basicas = [
            "icon.png",
            "fumaca.png",
            "explosion.png",
            "fire.png",
            "smoke.png",
            "rain.png",
            "banana.png",
            "crosshair.png",
            "sky.jpg",
            "clouds.jpg",
            "brick.jpg",
            "metal.jpg",
            "wood.jpg",
            "grass.jpg",
            # Texturas em português que o jogo procura
            "fogo.png",
            "explosao.png",
            "onda_choque.png"
        ]
        
        # Verifica e cria cada textura
        for nome_textura in texturas_basicas:
            caminho_textura = os.path.join(self.diretorio_texturas, nome_textura)
            if not os.path.exists(caminho_textura):
                print(f"Criando textura básica: {nome_textura}")
                if nome_textura == "icon.png":
                    self._criar_icone_basico(caminho_textura)
                else:
                    self._criar_textura_basica(caminho_textura, nome_textura)
            else:
                print(f"Textura existente: {nome_textura}")
            
    def _criar_icone_basico(self, caminho):
        """Cria um ícone básico para o jogo"""
        try:
            from PIL import Image, ImageDraw
            
            # Cria uma imagem de 256x256 pixels
            img = Image.new('RGBA', (256, 256), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Desenha um gorila estilizado (círculo marrom com detalhes)
            # Corpo
            draw.ellipse((48, 48, 208, 208), fill=(139, 69, 19, 255))
            
            # Cabeça
            draw.ellipse((88, 28, 168, 108), fill=(139, 69, 19, 255))
            
            # Olhos
            draw.ellipse((108, 48, 118, 58), fill=(255, 255, 255, 255))
            draw.ellipse((138, 48, 148, 58), fill=(255, 255, 255, 255))
            
            # Boca
            draw.arc((108, 68, 148, 88), 0, 180, fill=(255, 255, 255, 255), width=2)
            
            # Salva a imagem
            img.save(caminho)
            print(f"Ícone básico criado em: {caminho}")
        except ImportError:
            print("Não foi possível criar o ícone, PIL não está disponível")
            # Cria um arquivo vazio como placeholder
            with open(caminho, 'wb') as f:
                f.write(b'')

    def _criar_textura_basica(self, caminho, nome_textura):
        """Cria uma textura básica"""
        try:
            from PIL import Image, ImageDraw
            
            # Determina o tipo de textura a ser criada
            if nome_textura.endswith('.png'):
                # Texturas com transparência
                width, height = 128, 128
                img = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                
                if 'fumaca' in nome_textura or 'smoke' in nome_textura:
                    # Textura de fumaça - círculo branco com transparência
                    draw.ellipse((10, 10, width-10, height-10), fill=(255, 255, 255, 150))
                    
                elif 'explosion' in nome_textura or 'explosao' in nome_textura or 'fire' in nome_textura or 'fogo' in nome_textura:
                    # Textura de explosão - círculo laranja/vermelho
                    for i in range(20, 0, -5):
                        # Gradiente do centro para fora
                        color = (255, 128-i*5, 0, 200-i*10)
                        draw.ellipse((i, i, width-i, height-i), fill=color)
                        
                elif 'banana' in nome_textura:
                    # Textura de banana - oval amarela
                    draw.ellipse((20, 40, width-20, height-40), fill=(255, 255, 0, 255))
                    
                elif 'crosshair' in nome_textura:
                    # Textura de mira - círculo com cruz
                    draw.ellipse((20, 20, width-20, height-20), outline=(255, 0, 0, 255), width=2)
                    draw.line((width//2, 10, width//2, height-10), fill=(255, 0, 0, 255), width=2)
                    draw.line((10, height//2, width-10, height//2), fill=(255, 0, 0, 255), width=2)
                    
                elif 'rain' in nome_textura:
                    # Textura de chuva - linhas verticais
                    for i in range(0, width, 10):
                        draw.line((i, 0, i-20, height), fill=(200, 200, 255, 150), width=1)
                        
                elif 'onda_choque' in nome_textura:
                    # Textura de onda de choque - círculos concêntricos
                    draw.ellipse((5, 5, width-5, height-5), outline=(255, 255, 255, 200), width=2)
                    draw.ellipse((15, 15, width-15, height-15), outline=(255, 255, 255, 150), width=2)
                    draw.ellipse((25, 25, width-25, height-25), outline=(255, 255, 255, 100), width=2)
                    draw.ellipse((35, 35, width-35, height-35), outline=(255, 255, 255, 50), width=2)
                
            else:  # .jpg
                # Texturas sem transparência
                width, height = 256, 256
                img = Image.new('RGB', (width, height), color=(128, 128, 128))
                draw = ImageDraw.Draw(img)
                
                if 'sky' in nome_textura:
                    # Textura de céu - azul gradiente
                    for y in range(height):
                        # Gradiente do topo (azul claro) para o fundo (azul escuro)
                        blue = int(150 + (y / height) * 100)
                        for x in range(width):
                            img.putpixel((x, y), (100, 150, blue))
                            
                elif 'clouds' in nome_textura:
                    # Textura de nuvens - branco com cinza
                    img = Image.new('RGB', (width, height), color=(230, 230, 255))
                    # Adiciona manchas mais brancas para nuvens
                    for _ in range(20):
                        x = int(width * 0.1 + width * 0.8 * (random.random()))
                        y = int(height * 0.1 + height * 0.8 * (random.random()))
                        r = int(20 + 40 * random.random())
                        draw.ellipse((x-r, y-r, x+r, y+r), fill=(255, 255, 255))
                        
                elif 'brick' in nome_textura:
                    # Textura de tijolo - padrão de tijolos
                    brick_color = (180, 60, 40)
                    mortar_color = (200, 200, 200)
                    img = Image.new('RGB', (width, height), mortar_color)
                    
                    # Desenha padrão de tijolos
                    brick_h, brick_w = 20, 40
                    for y in range(0, height, brick_h):
                        offset = 0 if (y // brick_h) % 2 == 0 else brick_w // 2
                        for x in range(-offset, width, brick_w):
                            draw.rectangle((x+1, y+1, x+brick_w-1, y+brick_h-1), fill=brick_color)
                            
                elif 'metal' in nome_textura:
                    # Textura de metal - cinza com estrias
                    img = Image.new('RGB', (width, height), (180, 180, 190))
                    # Adiciona estrias metálicas
                    for y in range(0, height, 2):
                        color = 150 + int(random.random() * 50)
                        draw.line((0, y, width, y), fill=(color, color, color+10))
                        
                elif 'wood' in nome_textura:
                    # Textura de madeira - marrom com linhas
                    img = Image.new('RGB', (width, height), (120, 80, 40))
                    # Adiciona veios da madeira
                    for i in range(20):
                        y_pos = int(random.random() * height)
                        color = (100 + int(random.random() * 40), 
                                 60 + int(random.random() * 30), 
                                 20 + int(random.random() * 20))
                        draw.line((0, y_pos, width, y_pos+int(random.random()*20)-10), 
                                  fill=color, width=1+int(random.random()*3))
                                  
                elif 'grass' in nome_textura:
                    # Textura de grama - verde com pontos
                    img = Image.new('RGB', (width, height), (40, 140, 40))
                    # Adiciona pontos para textura de grama
                    for _ in range(5000):
                        x = int(random.random() * width)
                        y = int(random.random() * height)
                        color = (0, 100 + int(random.random() * 80), 0)
                        img.putpixel((x, y), color)
            
            # Salva a imagem
            img.save(caminho)
            print(f"Textura básica criada em: {caminho}")
        except ImportError:
            print(f"Não foi possível criar a textura {nome_textura}, PIL não está disponível")
            # Cria um arquivo vazio como placeholder
            with open(caminho, 'wb') as f:
                f.write(b'')
            
    def _verificar_e_criar_sons(self):
        """Verifica e cria sons básicos"""
        print("Verificando sons básicos...")
        
        # Lista de sons básicos para verificar
        sons_basicos = [
            "explosion.wav",
            "banana_throw.wav",
            "victory.wav",
            "thunder.wav",
            "menu_music.wav",
            "game_music.wav",
            "game_over_music.wav",
            "building_hit.wav",
            "gorilla_hit.wav",
            "menu_select.wav",
            "menu_confirm.wav",
            "wind.wav",
            "rain.wav"
        ]
        
        # Verifica e cria cada som
        for nome_som in sons_basicos:
            caminho_som = os.path.join(self.diretorio_sons, nome_som)
            if not os.path.exists(caminho_som):
                print(f"Criando som básico: {nome_som}")
                self._criar_som_basico(caminho_som)
            else:
                print(f"Som existente: {nome_som}")
                
    def _criar_som_basico(self, caminho):
        """Cria um arquivo de som básico (WAV com um segundo de silêncio)"""
        try:
            # Tenta usar o numpy para criar um arquivo WAV com 1 segundo de silêncio
            import numpy as np
            from scipy.io import wavfile
            
            # Cria um segundo de silêncio (44100 amostras)
            sr = 44100
            audio = np.zeros(sr, dtype=np.int16)
            
            # Salva como arquivo WAV
            wavfile.write(caminho, sr, audio)
            print(f"Som básico criado em: {caminho}")
        except ImportError:
            # Se não tiver scipy, cria um arquivo WAV manualmente
            with open(caminho, 'wb') as f:
                # Cabeçalho RIFF
                f.write(b'RIFF')           # ChunkID
                f.write(b'\x2C\x00\x00\x00')  # ChunkSize (44 bytes + 8 bytes de dados)
                f.write(b'WAVE')           # Format
                
                # Subchunk1 (fmt)
                f.write(b'fmt ')           # Subchunk1ID
                f.write(b'\x10\x00\x00\x00')  # Subchunk1Size (16 bytes)
                f.write(b'\x01\x00')       # AudioFormat (1 = PCM)
                f.write(b'\x01\x00')       # NumChannels (1 = mono)
                f.write(b'\x44\xAC\x00\x00')  # SampleRate (44100)
                f.write(b'\x44\xAC\x00\x00')  # ByteRate (44100)
                f.write(b'\x01\x00')       # BlockAlign (1)
                f.write(b'\x08\x00')       # BitsPerSample (8)
                
                # Subchunk2 (data)
                f.write(b'data')           # Subchunk2ID
                f.write(b'\x08\x00\x00\x00')  # Subchunk2Size (8 bytes)
                
                # 8 bytes de dados (silêncio)
                f.write(b'\x80\x80\x80\x80\x80\x80\x80\x80')
                
            print(f"Som básico criado em: {caminho}")

if __name__ == "__main__":
    verificador = VerificadorRecursos()
    verificador.verificar_e_criar_recursos()
