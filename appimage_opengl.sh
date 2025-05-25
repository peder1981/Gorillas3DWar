#!/bin/bash
# Script para criar um AppImage do Gorillas 3D War com suporte a OpenGL

echo "=== Criando AppImage do Gorillas 3D War (Com Suporte OpenGL) ==="

# Primeiro, vamos corrigir o arquivo effects.py diretamente
echo "Corrigindo o arquivo effects.py..."

# Backup do arquivo original
cp src/effects.py src/effects.py.bak

# Localizando a função problemática e substituindo-a
EFFECTS_FILE="src/effects.py"
TEMP_FILE="src/effects.py.temp"

# Criando o arquivo effects_replacement.py com a função corrigida
cat > effects_replacement.py << 'EOF'
    def criar_explosao(self, posicao, raio=2.0, num_particulas=50, tipo='padrao'):
        """
        Cria uma explosão na posição especificada com vários efeitos visuais.
        
        Args:
            posicao: Posição da explosão.
            raio: Raio da explosão.
            num_particulas: Número de partículas a serem criadas.
            tipo: Tipo de explosão ('padrao', 'grande', 'pequena', 'fogo').
        
        Returns:
            Dicionário com informações da explosão.
        """
        # Ajusta parâmetros baseados no tipo de explosão
        if tipo == 'grande':
            raio *= 2.0
            num_particulas *= 2
            duracao = 3.0
            cor_base = (1.0, 0.6, 0.0)  # Laranja mais intenso
            num_fragmentos = 20
            forca_fisica = 1000.0
        elif tipo == 'pequena':
            raio *= 0.6
            num_particulas = max(10, num_particulas // 2)
            duracao = 1.0
            cor_base = (1.0, 0.8, 0.2)  # Amarelo
            num_fragmentos = 0
            forca_fisica = 200.0
        elif tipo == 'fogo':
            raio *= 1.2
            duracao = 4.0
            cor_base = (0.9, 0.3, 0.1)  # Vermelho mais intenso
            num_fragmentos = 5
            forca_fisica = 500.0
        else:  # padrao
            duracao = 2.0
            cor_base = (1.0, 0.5, 0.0)  # Laranja padrão
            num_fragmentos = 10
            forca_fisica = 500.0
        
        # Cria nó para a explosão na hierarquia correta
        explosao_node = NodePath(f"explosao_{len(self.explosoes)}")
        explosao_node.reparentTo(self.explosoes_node)
        explosao_node.setPos(posicao)
        
        # Inicializa o dicionário da explosão
        explosao = {
            'node': explosao_node,
            'posicao': LPoint3(*posicao),
            'raio': raio,
            'tempo_vida': duracao,
            'tempo_inicial': duracao,
            'tipo': tipo
        }
        
        # Adiciona luzes para a explosão
        luzes = self._criar_luzes_explosao(explosao_node, cor_base, raio)
        explosao['luzes'] = luzes
        
        # Cria a onda de choque (esfera que expande)
        onda_choque = self._criar_onda_choque(explosao_node, cor_base, raio)
        explosao['onda_choque'] = onda_choque
        
        # Cria o flash de luz inicial
        flash = self._criar_flash_explosao(explosao_node, cor_base, raio)
        explosao['flash'] = flash
        
        # Cria as partículas de explosão
        particulas = self._criar_particulas_explosao(explosao_node, num_particulas, raio, cor_base, duracao)
        explosao['particulas'] = particulas
        
        # Cria centelhas
        num_centelhas = max(5, int(num_particulas * 0.3))
        centelhas = self._criar_centelhas_explosao(explosao_node, num_centelhas, raio)
        explosao['centelhas'] = centelhas
        
        # Cria fumaça
        num_nuvens_fumaca = max(3, int(num_particulas * 0.2))
        self._criar_fumaca_explosao(explosao, num_nuvens_fumaca, raio, duracao)
        
        # Aplica efeitos de física se o sistema estiver disponível
        if self.sistema_fisica and self.usar_fisica_avancada:
            # Aplica força de explosão a objetos próximos
            self.sistema_fisica.aplicar_forca_explosao(
                posicao, raio * 2.0, forca_fisica, afetar_predios=(tipo == 'grande')
            )
            
            # Cria fragmentos se for uma explosão grande
            if num_fragmentos > 0:
                # Define o modelo para os fragmentos
                modelo_fragmento = "models/misc/box"
                
                # Cria fragmentos físicos
                fragmentos = self.sistema_fisica.criar_fragmentos_explosao(
                    posicao, modelo_fragmento, num_fragmentos, forca_fisica,
                    escala_fragmentos=0.2 * raio, tempo_vida=duracao
                )
                
                explosao['fragmentos_fisica'] = fragmentos
        
        # Adiciona à lista de explosões para ser gerenciada
        self.explosoes.append(explosao)
        
        # Atualiza estatísticas
        self.estatisticas['num_explosoes'] += 1
        self.estatisticas['num_particulas'] += len(particulas)
        if 'centelhas' in explosao:
            self.estatisticas['num_particulas'] += len(explosao['centelhas'])
        
        return explosao
EOF

# Usar Python para substituir a função no arquivo
python3 - << EOF
import re

# Lê o arquivo original
with open("$EFFECTS_FILE", "r") as f:
    content = f.read()

# Lê a nova implementação da função
with open("effects_replacement.py", "r") as f:
    replacement = f.read()

# Encontra o início e fim da função criar_explosao
pattern = r"    def criar_explosao\(self.*?(?=    def _criar_centelhas_explosao)"
flags = re.DOTALL  # Permite que . corresponda a quebras de linha

# Substitui a função
modified_content = re.sub(pattern, replacement, content, flags=flags)

# Escreve o conteúdo modificado
with open("$TEMP_FILE", "w") as f:
    f.write(modified_content)
EOF

# Verifica se a substituição foi bem-sucedida
if [ -f "$TEMP_FILE" ]; then
    mv "$TEMP_FILE" "$EFFECTS_FILE"
    echo "Arquivo effects.py corrigido com sucesso!"
else
    echo "Falha ao corrigir o arquivo effects.py. Usando o original."
fi

# Cria o script de entrada que define variáveis de ambiente para OpenGL
cat > entrada.sh << 'EOF'
#!/bin/bash

# Script de entrada para o AppImage do Gorillas 3D War
# Define variáveis de ambiente necessárias para OpenGL

# Configurações de ambiente para OpenGL
export LIBGL_DRIVERS_PATH=/usr/lib/x86_64-linux-gnu/dri:/usr/lib/dri
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
export PYTHONPATH="$APPDIR/usr/share/gorillas3dwar:$PYTHONPATH"

# Inicia o jogo
cd "$APPDIR/usr/share/gorillas3dwar"
python3 iniciar.py
EOF

# Agora, criamos o AppImage
echo "Criando o AppImage..."

# Diretório de trabalho
TRABALHO="AppDir"
mkdir -p "$TRABALHO"

# Estrutura de diretórios do AppImage
mkdir -p "$TRABALHO/usr/bin"
mkdir -p "$TRABALHO/usr/share/gorillas3dwar"
mkdir -p "$TRABALHO/usr/share/applications"
mkdir -p "$TRABALHO/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$TRABALHO/usr/lib"

# Copia os arquivos do jogo
echo "Copiando arquivos do jogo..."
cp -r src "$TRABALHO/usr/share/gorillas3dwar/"
if [ -f "main.py" ]; then
    cp main.py "$TRABALHO/usr/share/gorillas3dwar/"
fi

# Cria diretórios para recursos se existirem
for dir in models textures sounds assets; do
    if [ -d "$dir" ]; then
        mkdir -p "$TRABALHO/usr/share/gorillas3dwar/$dir"
        cp -r "$dir"/* "$TRABALHO/usr/share/gorillas3dwar/$dir/" 2>/dev/null || true
    fi
done

# Cria o arquivo iniciar.py antes de empacotar
cat > "$TRABALHO/usr/share/gorillas3dwar/iniciar.py" << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

# Adiciona diretórios ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Verifica dependências antes de iniciar
try:
    import panda3d
except ImportError:
    print("Panda3D não está instalado. Instalando...")
    import subprocess
    subprocess.run(["pip3", "install", "panda3d"])

# Importa e executa o jogo
from main import main
main()
EOF

# Torna o arquivo iniciar.py executável
chmod +x "$TRABALHO/usr/share/gorillas3dwar/iniciar.py"

# Copia bibliotecas necessárias para OpenGL
if [ -d "/usr/lib/x86_64-linux-gnu/dri" ]; then
    mkdir -p "$TRABALHO/usr/lib/dri"
    cp -L /usr/lib/x86_64-linux-gnu/dri/*.so "$TRABALHO/usr/lib/dri/" 2>/dev/null || true
fi

# Cria o script wrapper
cp entrada.sh "$TRABALHO/usr/bin/gorillas3dwar"
chmod +x "$TRABALHO/usr/bin/gorillas3dwar"

# Cria o arquivo .desktop no diretório correto para o AppImage
cat > "$TRABALHO/gorillas3dwar.desktop" << EOF
[Desktop Entry]
Name=Gorillas 3D War
Comment=Um jogo de artilharia 3D inspirado no clássico Gorillas
Exec=gorillas3dwar
Icon=gorillas3dwar
Terminal=false
Type=Application
Categories=Game;ActionGame;
EOF

# Também coloca o desktop file no local usual
mkdir -p "$TRABALHO/usr/share/applications/"
cp "$TRABALHO/gorillas3dwar.desktop" "$TRABALHO/usr/share/applications/"

# Prepara o ícone para o AppImage
echo "Copiando ícones..."

# Primeiro cria pasta de ícones se não existir
mkdir -p "$TRABALHO/usr/share/icons/hicolor/256x256/apps/"

# Verifica e copia os ícones
if [ -f "textures/icon.png" ]; then
    echo "Usando ícone existente: textures/icon.png"
    cp "textures/icon.png" "$TRABALHO/usr/share/icons/hicolor/256x256/apps/gorillas3dwar.png"
    # Também copia o ícone para o diretório raiz (necessário para AppImage)
    cp "textures/icon.png" "$TRABALHO/gorillas3dwar.png"
else
    echo "Aviso: Ícone principal não encontrado."
    
    # Verifica se existe algum ícone na pasta icons
    if [ -f "textures/icons/icon_256.png" ]; then
        echo "Usando ícone alternativo: textures/icons/icon_256.png"
        cp "textures/icons/icon_256.png" "$TRABALHO/usr/share/icons/hicolor/256x256/apps/gorillas3dwar.png"
        cp "textures/icons/icon_256.png" "$TRABALHO/gorillas3dwar.png"
    else
        echo "Nenhum ícone encontrado. Criando um ícone vazio."
        # Cria um arquivo vazio como último recurso
        touch "$TRABALHO/usr/share/icons/hicolor/256x256/apps/gorillas3dwar.png"
        touch "$TRABALHO/gorillas3dwar.png"
    fi
fi

# Cria o AppRun
cat > "$TRABALHO/AppRun" << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
APPDIR=${SELF%/*}
export PATH="$APPDIR/usr/bin:$PATH"
export PYTHONPATH="$APPDIR/usr/share/gorillas3dwar:$PYTHONPATH"
export LIBGL_DRIVERS_PATH="$APPDIR/usr/lib/dri:$LIBGL_DRIVERS_PATH"
export LD_LIBRARY_PATH="$APPDIR/usr/lib:$LD_LIBRARY_PATH"

# Configuração adicional para OpenGL
export MESA_GLSL_CACHE_DISABLE=true
export LIBGL_DEBUG=verbose

gorillas3dwar "$@"
EOF

chmod +x "$TRABALHO/AppRun"

# Verifica se appimagetool está disponível
if ! command -v appimagetool &> /dev/null; then
    echo "appimagetool não encontrado. Baixando..."
    wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage -O appimagetool
    chmod +x appimagetool
    APPIMAGETOOL="./appimagetool"
else
    APPIMAGETOOL="appimagetool"
fi

# Cria o AppImage
echo "Criando AppImage OpenGL..."
$APPIMAGETOOL "$TRABALHO" "Gorillas3DWar-OpenGL-x86_64.AppImage"

echo "AppImage criado: Gorillas3DWar-OpenGL-x86_64.AppImage"
echo "Limpando arquivos temporários..."
rm -rf "$TRABALHO"
rm -f effects_replacement.py
rm -f entrada.sh

echo "Processo concluído!"
