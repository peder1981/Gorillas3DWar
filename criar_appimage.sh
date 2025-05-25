#!/bin/bash
# Script para criar um AppImage do Gorillas 3D War

echo "=== Criando AppImage do Gorillas 3D War ==="

# Diretório de trabalho
TRABALHO="AppDir"
mkdir -p "$TRABALHO"

# Estrutura de diretórios do AppImage
mkdir -p "$TRABALHO/usr/bin"
mkdir -p "$TRABALHO/usr/share/gorillas3dwar"
mkdir -p "$TRABALHO/usr/share/applications"
mkdir -p "$TRABALHO/usr/share/icons/hicolor/256x256/apps"

# Copia os arquivos do jogo
echo "Copiando arquivos do jogo..."
cp -r dist/Gorillas3DWar/* "$TRABALHO/usr/share/gorillas3dwar/"

# Cria o script wrapper
cat > "$TRABALHO/usr/bin/gorillas3dwar" << EOF
#!/bin/bash
# Wrapper para o Gorillas 3D War

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python 3 não está instalado. Por favor, instale-o primeiro."
    exit 1
fi

# Verifica se Panda3D está instalado
python3 -c "import panda3d" 2> /dev/null
if [ \$? -ne 0 ]; then
    echo "Panda3D não está instalado. Instalando..."
    pip3 install panda3d
fi

# Executa o jogo
cd "\$APPDIR/usr/share/gorillas3dwar"
python3 iniciar.py
EOF

# Torna o script executável
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
cat > "$TRABALHO/AppRun" << EOF
#!/bin/bash
SELF=\$(readlink -f "\$0")
APPDIR=\${SELF%/*}
export PATH="\$APPDIR/usr/bin:\$PATH"
export PYTHONPATH="\$APPDIR/usr/share/gorillas3dwar:\$PYTHONPATH"
gorillas3dwar "\$@"
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
echo "Criando AppImage..."
$APPIMAGETOOL "$TRABALHO" "Gorillas3DWar-x86_64.AppImage"

echo "AppImage criado: Gorillas3DWar-x86_64.AppImage"
echo "Limpando arquivos temporários..."
rm -rf "$TRABALHO"

echo "Processo concluído!"
