#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar um ícone para o Gorillas 3D War
"""
import os
from PIL import Image, ImageDraw, ImageFont

def criar_icone(tamanho=256, salvar_como="textures/icon.png"):
    """Cria um ícone simples para o jogo"""
    
    # Cria uma nova imagem com fundo transparente
    icone = Image.new('RGBA', (tamanho, tamanho), (0, 0, 0, 0))
    
    # Objeto para desenhar na imagem
    desenho = ImageDraw.Draw(icone)
    
    # Define cores
    cor_gorila = (80, 50, 20, 255)        # Marrom
    cor_banana = (255, 220, 0, 255)       # Amarelo
    cor_contorno = (40, 40, 40, 255)      # Cinza escuro
    cor_explosao = (255, 90, 0, 255)      # Laranja
    
    # Desenha o círculo de fundo
    raio = tamanho * 0.45
    centro = (tamanho // 2, tamanho // 2)
    desenho.ellipse(
        [(centro[0] - raio, centro[1] - raio), 
         (centro[0] + raio, centro[1] + raio)], 
        fill=(50, 120, 200, 200)  # Azul claro semi-transparente
    )
    
    # Desenha silhueta de gorila
    # (simplificada como forma geométrica)
    altura_gorila = tamanho * 0.6
    largura_gorila = altura_gorila * 0.6
    topo_gorila = centro[1] - altura_gorila * 0.4
    
    # Corpo principal
    desenho.ellipse(
        [(centro[0] - largura_gorila * 0.4, topo_gorila), 
         (centro[0] + largura_gorila * 0.4, topo_gorila + altura_gorila * 0.7)], 
        fill=cor_gorila, outline=cor_contorno, width=2
    )
    
    # Cabeça
    desenho.ellipse(
        [(centro[0] - largura_gorila * 0.3, topo_gorila - altura_gorila * 0.25), 
         (centro[0] + largura_gorila * 0.3, topo_gorila + altura_gorila * 0.15)], 
        fill=cor_gorila, outline=cor_contorno, width=2
    )
    
    # Desenha banana
    banana_centro = (centro[0] + tamanho * 0.25, centro[1] - tamanho * 0.15)
    banana_largura = tamanho * 0.2
    banana_altura = banana_largura * 0.4
    
    # Banana (forma curva simplificada como elipse)
    desenho.ellipse(
        [(banana_centro[0] - banana_largura * 0.5, banana_centro[1] - banana_altura * 0.5), 
         (banana_centro[0] + banana_largura * 0.5, banana_centro[1] + banana_altura * 0.5)], 
        fill=cor_banana, outline=cor_contorno, width=2
    )
    
    # Explosão ao redor da banana
    desenho.ellipse(
        [(banana_centro[0] - banana_largura * 0.7, banana_centro[1] - banana_altura * 0.7), 
         (banana_centro[0] + banana_largura * 0.7, banana_centro[1] + banana_altura * 0.7)], 
        outline=cor_explosao, width=3
    )
    
    # Raios da explosão
    for i in range(8):
        angulo = i * 45
        import math
        x1 = banana_centro[0] + math.cos(math.radians(angulo)) * banana_largura * 0.7
        y1 = banana_centro[1] + math.sin(math.radians(angulo)) * banana_altura * 0.7
        x2 = banana_centro[0] + math.cos(math.radians(angulo)) * banana_largura * 1.1
        y2 = banana_centro[1] + math.sin(math.radians(angulo)) * banana_altura * 1.1
        desenho.line([(x1, y1), (x2, y2)], fill=cor_explosao, width=3)
    
    # Garante que o diretório existe
    os.makedirs(os.path.dirname(salvar_como), exist_ok=True)
    
    # Salva o ícone
    icone.save(salvar_como)
    
    # Também cria uma versão para Windows (.ico)
    if salvar_como.endswith(".png"):
        ico_path = salvar_como.replace(".png", ".ico")
        icone.save(ico_path)
    
    print(f"Ícone criado com sucesso: {salvar_como}")
    return salvar_como

def criar_icones_multiplas_resolucoes():
    """Cria ícones em várias resoluções para diferentes plataformas"""
    tamanhos = [16, 32, 48, 64, 128, 256, 512]
    
    # Cria diretório para ícones
    os.makedirs("textures/icons", exist_ok=True)
    
    # Cria o ícone base em 512px
    icone_base = criar_icone(512, "textures/icons/icon_512.png")
    
    # Carrega o ícone base
    imagem_base = Image.open(icone_base)
    
    # Redimensiona para outros tamanhos
    for tamanho in tamanhos:
        if tamanho == 512:
            continue  # Já criamos o de 512px
            
        nome_arquivo = f"textures/icons/icon_{tamanho}.png"
        imagem_redimensionada = imagem_base.resize((tamanho, tamanho), Image.Resampling.LANCZOS)
        imagem_redimensionada.save(nome_arquivo)
        print(f"Ícone criado: {nome_arquivo}")
    
    # Copia o ícone de 256px como ícone principal
    imagem_256 = Image.open("textures/icons/icon_256.png")
    imagem_256.save("textures/icon.png")
    
    # Cria um ícone .ico para Windows (contém múltiplas resoluções)
    icone_windows = "textures/icon.ico"
    icones_para_ico = []
    for tamanho in [16, 32, 48, 64, 128, 256]:
        icones_para_ico.append(Image.open(f"textures/icons/icon_{tamanho}.png"))
    
    icones_para_ico[0].save(
        icone_windows, 
        format="ICO", 
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    )
    print(f"Ícone Windows criado: {icone_windows}")
    
    # Tenta criar ícone .icns para macOS se o sistema tiver o utilitário
    try:
        import subprocess
        iconset_dir = "textures/icons.iconset"
        os.makedirs(iconset_dir, exist_ok=True)
        
        # Copia os ícones para o formato necessário
        for tamanho in [16, 32, 64, 128, 256, 512]:
            shutil.copy(
                f"textures/icons/icon_{tamanho}.png", 
                f"{iconset_dir}/icon_{tamanho}x{tamanho}.png"
            )
            if tamanho <= 256:  # Também cria versões @2x
                shutil.copy(
                    f"textures/icons/icon_{tamanho*2 if tamanho*2 <= 512 else 512}.png", 
                    f"{iconset_dir}/icon_{tamanho}x{tamanho}@2x.png"
                )
        
        # Usa o iconutil do macOS para criar o .icns
        subprocess.run(["iconutil", "-c", "icns", iconset_dir])
        print("Ícone macOS criado: textures/icons.icns")
    except:
        print("Não foi possível criar o ícone .icns para macOS (requer macOS com iconutil)")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--multiplos":
        criar_icones_multiplas_resolucoes()
    else:
        criar_icone()
