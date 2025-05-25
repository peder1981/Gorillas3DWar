#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gorillas 3D War - Versão Pygame Aprimorada
"""
import pygame
import sys
import math
import random
from pygame.locals import *

# Inicialização
pygame.init()
LARGURA_TELA = 800
ALTURA_TELA = 600
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Gorillas 3D War")
relogio = pygame.time.Clock()

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
AZUL = (100, 149, 237)
VERDE = (0, 255, 0)
VERMELHO = (255, 0, 0)
AMARELO = (255, 255, 0)
MARROM = (139, 69, 19)
MARROM_CLARO = (160, 120, 90)
CINZA = (169, 169, 169)

# Parâmetros do jogo
gravidade = 0.5
vento = random.uniform(-0.3, 0.3)
jogador_atual = 0
angulo = 45
forca = 50
pontuacao = [0, 0]
MAX_PONTUACAO = 3
explosoes = []

# Fontes
fonte_pequena = pygame.font.SysFont("Arial", 20)
fonte_media = pygame.font.SysFont("Arial", 30)
fonte_grande = pygame.font.SysFont("Arial", 50)

# Classe Gorila
class Gorila(pygame.sprite.Sprite):
    def __init__(self, x, y, cor):
        super().__init__()
        self.image = pygame.Surface((60, 80), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.saude = 100
        self.cor = cor
        self.direcao = 1 if cor == VERMELHO else -1
        
    def desenhar(self):
        # Corpo
        pygame.draw.ellipse(tela, MARROM, (self.rect.x + 10, self.rect.y + 30, 40, 50))
        
        # Braços
        ombro_x = self.rect.x + 25
        ombro_y = self.rect.y + 45
        
        # Braço esquerdo
        pygame.draw.line(tela, MARROM, (ombro_x, ombro_y), 
                         (ombro_x - 15 * self.direcao, ombro_y + 20), 10)
        
        # Braço direito (que segura a banana)
        pygame.draw.line(tela, MARROM, (ombro_x, ombro_y), 
                         (ombro_x + 25 * self.direcao, ombro_y + 10), 10)
        
        # Pernas
        quadril_x = self.rect.x + 30
        quadril_y = self.rect.y + 75
        
        pygame.draw.line(tela, MARROM, (quadril_x - 10, quadril_y), 
                         (quadril_x - 15, quadril_y + 20), 12)
        pygame.draw.line(tela, MARROM, (quadril_x + 10, quadril_y), 
                         (quadril_x + 15, quadril_y + 20), 12)
        
        # Cabeça
        pygame.draw.circle(tela, MARROM, (self.rect.centerx, self.rect.top + 20), 25)
        
        # Detalhes do rosto
        face_dir = self.direcao
        
        # Olhos
        olho_x = 8 * face_dir
        
        pygame.draw.circle(tela, BRANCO, (self.rect.centerx - olho_x, self.rect.top + 15), 8)
        pygame.draw.circle(tela, BRANCO, (self.rect.centerx + olho_x, self.rect.top + 15), 8)
        
        pygame.draw.circle(tela, PRETO, (self.rect.centerx - olho_x, self.rect.top + 15), 4)
        pygame.draw.circle(tela, PRETO, (self.rect.centerx + olho_x, self.rect.top + 15), 4)
        
        # Reflexo nos olhos
        pygame.draw.circle(tela, BRANCO, (self.rect.centerx - olho_x + 2, self.rect.top + 13), 2)
        pygame.draw.circle(tela, BRANCO, (self.rect.centerx + olho_x + 2, self.rect.top + 13), 2)
        
        # Nariz
        pygame.draw.circle(tela, MARROM_CLARO, (self.rect.centerx, self.rect.top + 25), 8)
        pygame.draw.circle(tela, PRETO, (self.rect.centerx - 3 * face_dir, self.rect.top + 25), 2)
        pygame.draw.circle(tela, PRETO, (self.rect.centerx + 3 * face_dir, self.rect.top + 25), 2)
        
        # Boca
        boca_x = self.rect.centerx
        boca_y = self.rect.top + 35
        
        pygame.draw.arc(tela, (200, 100, 100), (boca_x - 15, boca_y - 5, 30, 15), 0, math.pi, 3)
        
        # Indicação do jogador (coroa para o jogador atual)
        if (jogador_atual == 0 and self.cor == VERMELHO) or (jogador_atual == 1 and self.cor == VERDE):
            # Desenha coroa
            pontos_coroa = [
                (self.rect.centerx - 15, self.rect.top - 10),
                (self.rect.centerx - 10, self.rect.top - 20),
                (self.rect.centerx - 5, self.rect.top - 10),
                (self.rect.centerx, self.rect.top - 20),
                (self.rect.centerx + 5, self.rect.top - 10),
                (self.rect.centerx + 10, self.rect.top - 20),
                (self.rect.centerx + 15, self.rect.top - 10)
            ]
            pygame.draw.polygon(tela, AMARELO, pontos_coroa)
            pygame.draw.polygon(tela, PRETO, pontos_coroa, 2)
        
        pygame.draw.circle(tela, self.cor, (self.rect.centerx, self.rect.top - 30), 8)

# Classe Banana (projétil)
class Banana(pygame.sprite.Sprite):
    def __init__(self, x, y, angulo, forca, cor=AMARELO):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.angulo_rad = math.radians(angulo)
        self.velocidade_x = forca * math.cos(self.angulo_rad) * 0.3
        self.velocidade_y = -forca * math.sin(self.angulo_rad) * 0.3
        self.x = float(x)
        self.y = float(y)
        self.trajetoria = []
        self.rotacao = 0
        self.ultima_posicao = (x, y)
        
    def atualizar(self):
        self.ultima_posicao = (self.rect.centerx, self.rect.centery)
        self.velocidade_x += vento
        self.velocidade_y += gravidade
        self.x += self.velocidade_x
        self.y += self.velocidade_y
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        self.trajetoria.append((self.rect.centerx, self.rect.centery))
        self.rotacao = (self.rotacao + 8) % 360
        
        # Verifica colisão com as bordas
        if self.rect.bottom > ALTURA_TELA or self.rect.right < 0 or self.rect.left > LARGURA_TELA:
            self.kill()
    
    def desenhar(self):
        # Desenha rastro
        if len(self.trajetoria) > 1:
            for i in range(1, len(self.trajetoria)):
                inicio = self.trajetoria[i-1]
                fim = self.trajetoria[i]
                espessura = max(1, 4 - i//5)  # Diminui a espessura com o tempo
                alpha = max(20, 255 - i*10)  # Diminui a opacidade com o tempo
                cor_rastro = (255, 255, 0, alpha)
                pygame.draw.line(tela, cor_rastro, inicio, fim, espessura)
        
        # Desenha banana com forma de banana e rotação
        banana_pontos = []
        centro_x, centro_y = self.rect.center
        
        # Criar forma de banana
        for angulo in range(0, 360, 20):
            rad = math.radians(angulo + self.rotacao)
            # Usar equações paramétricas para criar forma de banana
            raio = 8
            if 90 < angulo < 270:
                raio = 6
            
            offset_x = 0
            if angulo > 180:
                offset_x = -2
            else:
                offset_x = 2
                
            x = centro_x + raio * math.cos(rad) + offset_x
            y = centro_y + raio * math.sin(rad)
            banana_pontos.append((x, y))
        
        # Desenha banana
        if len(banana_pontos) > 2:
            pygame.draw.polygon(tela, AMARELO, banana_pontos)
            pygame.draw.polygon(tela, (218, 165, 32), banana_pontos, 1)

# Classe Prédio
class Predio(pygame.sprite.Sprite):
    def __init__(self, x, largura, altura, cor=None):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        if cor is None:
            self.cor = (
                random.randint(100, 150),
                random.randint(100, 150),
                random.randint(150, 200)
            )
        else:
            self.cor = cor
        self.image.fill(self.cor)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, ALTURA_TELA)
        self.largura = largura
        self.altura = altura
        self.janelas_acesas = []
        
        # Gera algumas janelas aleatoriamente acesas
        num_janelas_x = int(largura / 20)
        num_janelas_y = int(altura / 30)
        for i in range(num_janelas_x):
            for j in range(num_janelas_y):
                if random.random() < 0.7:  # 70% de chance da janela estar acesa
                    self.janelas_acesas.append((i, j))
    
    def desenhar(self):
        pygame.draw.rect(tela, self.cor, self.rect)
        
        # Desenha contorno do prédio
        pygame.draw.rect(tela, (50, 50, 50), self.rect, 2)
        
        # Desenha textura no topo do prédio (telhado)
        pygame.draw.rect(tela, (70, 70, 70), 
                         (self.rect.left, self.rect.top, self.rect.width, 5))
        
        # Desenha janelas
        num_janelas_x = int(self.rect.width / 20)
        num_janelas_y = int(self.rect.height / 30)
        
        for i in range(num_janelas_x):
            for j in range(num_janelas_y):
                janela_x = self.rect.left + i*20 + 5
                janela_y = self.rect.top + j*30 + 5
                
                # Determina a cor da janela (acesa ou apagada)
                if (i, j) in self.janelas_acesas:
                    cor_janela = (255, 255, 190)
                else:
                    cor_janela = (50, 70, 120)
                
                # Desenha a janela
                pygame.draw.rect(tela, cor_janela, (janela_x, janela_y, 10, 20))
                pygame.draw.rect(tela, (40, 40, 40), (janela_x, janela_y, 10, 20), 1)

# Efeitos visuais
def criar_explosao(x, y):
    explosoes.append({"pos": (x, y), "raio": 5, "tempo": 20, "particulas": []})
    
    # Adiciona partículas à explosão
    for _ in range(20):
        angulo = random.uniform(0, math.pi * 2)
        velocidade = random.uniform(2, 8)
        raio = random.uniform(2, 6)
        cor = (
            random.randint(200, 255),
            random.randint(100, 200),
            random.randint(0, 100)
        )
        explosoes[-1]["particulas"].append({
            "pos": [x, y],
            "vel": [velocidade * math.cos(angulo), velocidade * math.sin(angulo)],
            "raio": raio,
            "cor": cor,
            "tempo": random.randint(20, 40)
        })

def atualizar_explosoes():
    for explosao in explosoes[:]:
        # Desenha o círculo principal
        if explosao["tempo"] > 0:
            transparencia = min(255, explosao["tempo"] * 12)
            cor_explosao = (255, 165, 0, transparencia)
            pygame.draw.circle(tela, cor_explosao, explosao["pos"], explosao["raio"])
            explosao["raio"] += 2
            explosao["tempo"] -= 1
        
        # Atualiza e desenha partículas
        for particula in explosao["particulas"][:]:
            particula["pos"][0] += particula["vel"][0]
            particula["pos"][1] += particula["vel"][1]
            particula["tempo"] -= 1
            
            # Adiciona gravidade às partículas
            particula["vel"][1] += 0.1
            
            if particula["tempo"] <= 0:
                explosao["particulas"].remove(particula)
            else:
                transparencia = min(255, particula["tempo"] * 6)
                cor = list(particula["cor"])
                if len(cor) == 3:
                    cor.append(transparencia)
                else:
                    cor[3] = transparencia
                
                pygame.draw.circle(tela, cor, 
                                  (int(particula["pos"][0]), int(particula["pos"][1])), 
                                  int(particula["raio"]))
        
        if explosao["tempo"] <= 0 and not explosao["particulas"]:
            explosoes.remove(explosao)

# Funções de desenho para o cenário
def desenhar_fundo():
    # Céu gradiente
    for y in range(ALTURA_TELA):
        # Cria um efeito de gradiente para o céu
        intensidade = 1 - (y / ALTURA_TELA)
        cor = (
            int(100 * intensidade), 
            int(150 * intensidade), 
            int(255 * intensidade)
        )
        pygame.draw.line(tela, cor, (0, y), (LARGURA_TELA, y))
    
    # Sol com efeito de brilho
    sol_x = LARGURA_TELA - 100
    sol_y = 80
    
    # Efeito de brilho
    for raio in range(80, 30, -10):
        transparencia = 100 - raio
        pygame.draw.circle(tela, (255, 255, 100, transparencia), (sol_x, sol_y), raio)
    
    # Sol principal
    pygame.draw.circle(tela, (255, 255, 180), (sol_x, sol_y), 40)
    pygame.draw.circle(tela, (255, 200, 50), (sol_x, sol_y), 35)
    
    # Nuvens com efeito 3D
    desenhar_nuvem(100, 120, 30)
    desenhar_nuvem(300, 80, 25)
    desenhar_nuvem(500, 150, 35)
    desenhar_nuvem(650, 100, 20)

def desenhar_nuvem(x, y, raio):
    # Base da nuvem
    pygame.draw.circle(tela, (220, 220, 220), (x, y), raio)
    pygame.draw.circle(tela, (230, 230, 230), (x + raio - 5, y - 5), raio - 3)
    pygame.draw.circle(tela, (240, 240, 240), (x - raio + 8, y - 2), raio - 5)
    pygame.draw.circle(tela, (250, 250, 250), (x - 5, y - raio + 5), raio - 10)
    
    # Contorno suave
    pygame.draw.circle(tela, (200, 200, 200), (x, y), raio, 1)
    pygame.draw.circle(tela, (200, 200, 200), (x + raio - 5, y - 5), raio - 3, 1)

# Funções do jogo
def desenhar_hud():
    # Painel de informações
    pygame.draw.rect(tela, (0, 0, 0, 180), (0, 0, LARGURA_TELA, 50))
    
    # Informações do jogador atual
    texto_jogador = fonte_media.render(f"Jogador {jogador_atual + 1}", True, BRANCO)
    tela.blit(texto_jogador, (20, 10))
    
    # Ângulo e força
    texto_angulo = fonte_pequena.render(f"Ângulo: {angulo}°", True, BRANCO)
    texto_forca = fonte_pequena.render(f"Força: {forca}", True, BRANCO)
    tela.blit(texto_angulo, (150, 10))
    tela.blit(texto_forca, (250, 10))
    
    # Vento
    direcao_vento = "←" if vento < 0 else "→" if vento > 0 else "-"
    intensidade = abs(vento) * 100
    texto_vento = fonte_pequena.render(f"Vento: {direcao_vento} {intensidade:.1f}%", True, BRANCO)
    tela.blit(texto_vento, (LARGURA_TELA - 150, 10))
    
    # Pontuação
    texto_pontuacao = fonte_pequena.render(f"Placar: {pontuacao[0]} - {pontuacao[1]}", True, BRANCO)
    tela.blit(texto_pontuacao, (LARGURA_TELA // 2 - 50, 10))
    
    # Indicadores de controle na parte inferior
    controles = fonte_pequena.render("Controles: ↑↓ = Ângulo   ←→ = Força   Espaço = Lançar", True, BRANCO)
    tela.blit(controles, (LARGURA_TELA // 2 - 180, ALTURA_TELA - 30))

def lancar_banana():
    global jogador_atual
    
    if jogador_atual == 0:
        x = gorila1.rect.right
        y = gorila1.rect.top + 15
    else:
        x = gorila2.rect.left
        y = gorila2.rect.top + 15
        
    banana = Banana(x, y, angulo if jogador_atual == 0 else 180 - angulo, forca)
    bananas.add(banana)

def verificar_colisao():
    global jogador_atual, vento, estado_jogo, pontuacao
    
    # Verifica colisão com prédios
    for banana in bananas:
        colisoes_predios = pygame.sprite.spritecollide(banana, predios, False)
        if colisoes_predios:
            criar_explosao(banana.rect.centerx, banana.rect.centery)
            banana.kill()
    
    # Verifica colisão com gorilas
    for banana in bananas:
        if jogador_atual == 0 and banana.rect.colliderect(gorila2.rect):
            criar_explosao(banana.rect.centerx, banana.rect.centery)
            banana.kill()
            pontuacao[0] += 1
            vento = random.uniform(-0.3, 0.3)
            
            if pontuacao[0] >= MAX_PONTUACAO:
                estado_jogo = "game_over"
            else:
                jogador_atual = 0  # Mantém o mesmo jogador após acertar
            return
            
        elif jogador_atual == 1 and banana.rect.colliderect(gorila1.rect):
            criar_explosao(banana.rect.centerx, banana.rect.centery)
            banana.kill()
            pontuacao[1] += 1
            vento = random.uniform(-0.3, 0.3)
            
            if pontuacao[1] >= MAX_PONTUACAO:
                estado_jogo = "game_over"
            else:
                jogador_atual = 1  # Mantém o mesmo jogador após acertar
            return
    
    # Se não há bananas no jogo, troca jogador
    if len(bananas) == 0:
        jogador_atual = 1 - jogador_atual  # Alterna entre 0 e 1

def reiniciar_jogo():
    global pontuacao, jogador_atual, vento, estado_jogo, explosoes
    pontuacao = [0, 0]
    jogador_atual = 0
    vento = random.uniform(-0.3, 0.3)
    estado_jogo = "jogando"
    explosoes = []

def mostrar_game_over():
    # Cria overlay translúcido
    overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    tela.blit(overlay, (0, 0))
    
    # Determina vencedor
    vencedor = "Jogador 1" if pontuacao[0] > pontuacao[1] else "Jogador 2"
    cor_vencedor = VERMELHO if vencedor == "Jogador 1" else VERDE
    
    # Desenha texto do vencedor com sombra
    texto_vencedor = fonte_grande.render(f"{vencedor} Venceu!", True, cor_vencedor)
    sombra_vencedor = fonte_grande.render(f"{vencedor} Venceu!", True, PRETO)
    
    # Desenha título com efeito de sombra
    titulo_x = LARGURA_TELA//2 - texto_vencedor.get_width()//2
    titulo_y = ALTURA_TELA//2 - 100
    tela.blit(sombra_vencedor, (titulo_x + 3, titulo_y + 3))
    tela.blit(texto_vencedor, (titulo_x, titulo_y))
    
    # Desenha pontuação
    texto_pontuacao = fonte_media.render(f"Placar: {pontuacao[0]} - {pontuacao[1]}", True, BRANCO)
    tela.blit(texto_pontuacao, (LARGURA_TELA//2 - texto_pontuacao.get_width()//2, ALTURA_TELA//2 - 50))
    
    # Botões
    pygame.draw.rect(tela, (80, 80, 80), (LARGURA_TELA//2 - 100, ALTURA_TELA//2 + 30, 200, 40), border_radius=5)
    pygame.draw.rect(tela, (60, 60, 60), (LARGURA_TELA//2 - 100, ALTURA_TELA//2 + 90, 200, 40), border_radius=5)
    
    # Texto botões
    texto_reiniciar = fonte_media.render("Reiniciar (R)", True, BRANCO)
    texto_sair = fonte_media.render("Sair (ESC)", True, BRANCO)
    
    tela.blit(texto_reiniciar, (LARGURA_TELA//2 - texto_reiniciar.get_width()//2, ALTURA_TELA//2 + 35))
    tela.blit(texto_sair, (LARGURA_TELA//2 - texto_sair.get_width()//2, ALTURA_TELA//2 + 95))

# Criar prédios
predios = pygame.sprite.Group()
num_predios = 5
for i in range(num_predios):
    altura = random.randint(100, 300)
    largura = random.randint(60, 100)
    x = i * (LARGURA_TELA // num_predios)
    predio = Predio(x, largura, altura)
    predios.add(predio)

# Criar gorilas
gorilas = []
gorila1 = Gorila(150, ALTURA_TELA - 350, VERMELHO)
gorila2 = Gorila(LARGURA_TELA - 150, ALTURA_TELA - 350, VERDE)
gorilas.append(gorila1)
gorilas.append(gorila2)

# Grupo de bananas (projéteis)
bananas = pygame.sprite.Group()

# Estado do jogo
estado_jogo = "jogando"  # jogando, game_over

# Loop principal
rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == QUIT:
            rodando = False
        
        elif estado_jogo == "jogando":
            if evento.type == KEYDOWN:
                if evento.key == K_UP:
                    angulo = min(angulo + 5, 90)
                elif evento.key == K_DOWN:
                    angulo = max(angulo - 5, 0)
                elif evento.key == K_RIGHT:
                    forca = min(forca + 5, 100)
                elif evento.key == K_LEFT:
                    forca = max(forca - 5, 10)
                elif evento.key == K_SPACE:
                    if len(bananas) == 0:  # Evita lançamentos múltiplos
                        lancar_banana()
        
        elif estado_jogo == "game_over":
            if evento.type == KEYDOWN:
                if evento.key == K_r:
                    reiniciar_jogo()
                elif evento.key == K_ESCAPE:
                    rodando = False
    
    # Atualiza
    if estado_jogo == "jogando":
        for banana in bananas:
            banana.atualizar()
        verificar_colisao()
    
    # Desenha
    desenhar_fundo()
    
    # Desenha prédios
    for predio in predios:
        predio.desenhar()
    
    # Desenha gorilas
    for gorila in gorilas:
        gorila.desenhar()
    
    # Desenha bananas
    for banana in bananas:
        banana.desenhar()
    
    # Atualiza e desenha explosões
    atualizar_explosoes()
    
    # Desenha HUD
    desenhar_hud()
    
    # Desenha tela de game over
    if estado_jogo == "game_over":
        mostrar_game_over()
    
    pygame.display.flip()
    relogio.tick(60)

pygame.quit()
sys.exit()
