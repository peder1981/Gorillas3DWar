#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para distribuição completa do jogo Gorillas 3D War para múltiplas plataformas
Faz correções necessárias e prepara os arquivos para distribuição
"""
import os
import sys
import platform
import subprocess
import shutil
import re
from pathlib import Path

class DistribuidorGorillas:
    """Classe para gerenciar a distribuição do jogo Gorillas 3D War para múltiplas plataformas"""
    
    def __init__(self):
        """Inicializa o distribuidor"""
        self.diretorio_base = os.path.dirname(os.path.abspath(__file__))
        self.diretorio_src = os.path.join(self.diretorio_base, "src")
        self.diretorio_tmp = os.path.join(self.diretorio_base, "tmp_dist")
        self.sistema = platform.system().lower()
        
        # Verifica se os diretórios necessários existem
        if not os.path.exists(self.diretorio_src):
            print(f"Erro: Diretório de código-fonte não encontrado: {self.diretorio_src}")
            sys.exit(1)
            
        # Cria o diretório temporário se não existir
        os.makedirs(self.diretorio_tmp, exist_ok=True)
        
    def verificar_dependencias(self):
        """Verifica se todas as dependências necessárias estão instaladas"""
        print("Verificando dependências...")
        
        try:
            import panda3d
            print("✓ Panda3D está instalado.")
        except ImportError:
            print("✗ Panda3D não está instalado. Instalando...")
            subprocess.run([sys.executable, "-m", "pip", "install", "panda3d"])
            
        # Verifica outras dependências específicas da plataforma
        if self.sistema == "linux":
            self._verificar_dependencias_linux()
        elif self.sistema == "windows":
            self._verificar_dependencias_windows()
        elif self.sistema == "darwin":
            self._verificar_dependencias_macos()
            
        print("Verificação de dependências concluída.")

    def _verificar_dependencias_linux(self):
        """Verifica dependências específicas do Linux"""
        # Verifica se appimagetool está disponível
        appimagetool_path = shutil.which("appimagetool")
        if not appimagetool_path:
            print("✗ appimagetool não encontrado. Será baixado durante o processo de empacotamento.")
        else:
            print(f"✓ appimagetool encontrado em: {appimagetool_path}")
            
    def _verificar_dependencias_windows(self):
        """Verifica dependências específicas do Windows"""
        # Verifica se NSIS está instalado (para criar instaladores)
        try:
            output = subprocess.check_output(["makensis", "/VERSION"], stderr=subprocess.STDOUT, text=True)
            print(f"✓ NSIS encontrado: {output.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("✗ NSIS não encontrado. Será necessário para criar instaladores Windows.")
            
    def _verificar_dependencias_macos(self):
        """Verifica dependências específicas do macOS"""
        # Verifica se é possível criar pacotes .app e .dmg
        if shutil.which("hdiutil"):
            print("✓ hdiutil encontrado para criação de DMG.")
        else:
            print("✗ hdiutil não encontrado. Pode haver problemas na criação de pacotes DMG.")

    def corrigir_arquivos(self):
        """Corrige problemas conhecidos nos arquivos do jogo"""
        print("Corrigindo arquivos do jogo...")
        
        # Corrige o problema de sintaxe no arquivo effects.py
        self._corrigir_effects_py()
        
        # Garante que as classes de compatibilidade existam
        self._adicionar_classes_compatibilidade()
        
        print("Correção de arquivos concluída.")
        
    def _corrigir_effects_py(self):
        """Corrige problemas no arquivo effects.py"""
        arquivo_effects = os.path.join(self.diretorio_src, "effects.py")
        arquivo_backup = arquivo_effects + ".bak"
        
        # Faz backup do arquivo original
        shutil.copy2(arquivo_effects, arquivo_backup)
        print(f"Backup criado em: {arquivo_backup}")
        
        # Lê o conteúdo do arquivo
        with open(arquivo_effects, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        
        # Procura pelo bloco da função criar_explosao
        inicio_criar_explosao = None
        fim_criar_explosao = None
        inicio_proxima_funcao = None
        
        for i, linha in enumerate(linhas):
            if re.match(r'\s*def criar_explosao\(', linha):
                inicio_criar_explosao = i
            elif inicio_criar_explosao is not None and re.match(r'\s*def _criar_centelhas_explosao\(', linha):
                inicio_proxima_funcao = i
                fim_criar_explosao = i - 1
                break
        
        if inicio_criar_explosao is None or fim_criar_explosao is None:
            print("Não foi possível localizar a função criar_explosao")
            return False
        
        print(f"Encontrada função criar_explosao nas linhas {inicio_criar_explosao} até {fim_criar_explosao}")
        
        # Verifica e corrige a indentação da função
        indentacao_base = re.match(r'^(\s*)', linhas[inicio_criar_explosao]).group(1)
        indentacao_corpo = indentacao_base + "    "  # Adiciona 4 espaços para o corpo da função
        
        # Garante que o 'return' tenha a indentação correta
        for i in range(inicio_criar_explosao, fim_criar_explosao + 1):
            linha = linhas[i]
            if 'return explosao' in linha:
                # Garante que a linha de return tenha a indentação correta
                linhas[i] = indentacao_corpo + "return explosao\n"
        
        # Garante que a próxima função tenha a indentação correta
        if inicio_proxima_funcao:
            linhas[inicio_proxima_funcao] = indentacao_base + "def _criar_centelhas_explosao(self, node_pai, num_centelhas, raio):\n"
        
        # Garante que não haja linhas em branco com indentação incorreta entre as funções
        for i in range(fim_criar_explosao + 1, inicio_proxima_funcao):
            if linhas[i].strip() == "":
                linhas[i] = "\n"
        
        # Escreve o arquivo corrigido
        with open(arquivo_effects, 'w', encoding='utf-8') as f:
            f.writelines(linhas)
        
        print("Arquivo effects.py corrigido com sucesso!")
        return True
        
    def _adicionar_classes_compatibilidade(self):
        """Adiciona classes de compatibilidade para garantir que as importações funcionem"""
        # Verifica e adiciona a classe ExplosionManager no arquivo effects.py
        arquivo_effects = os.path.join(self.diretorio_src, "effects.py")
        
        with open(arquivo_effects, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            
        # Verifica se a classe ExplosionManager já existe
        if "class ExplosionManager" not in conteudo:
            # Adiciona a classe ExplosionManager ao final do arquivo
            with open(arquivo_effects, 'a', encoding='utf-8') as f:
                f.write("\n\n# Classe para compatibilidade com o código existente\n")
                f.write("class ExplosionManager(EffectsSystem):\n")
                f.write("    \"\"\"Classe para compatibilidade com código existente que importa ExplosionManager.\n")
                f.write("    Esta classe herda todas as funcionalidades do EffectsSystem para manter\n")
                f.write("    compatibilidade com código que foi escrito para a versão anterior da API.\n")
                f.write("    \"\"\"\n")
                f.write("    pass\n")
            print("Classe ExplosionManager adicionada ao arquivo effects.py")
        
        # Verifica e adiciona a classe Game no arquivo game.py
        arquivo_game = os.path.join(self.diretorio_src, "game.py")
        
        with open(arquivo_game, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            
        # Verifica se a classe Game já existe
        if "class Game" not in conteudo:
            # Adiciona a classe Game ao final do arquivo
            with open(arquivo_game, 'a', encoding='utf-8') as f:
                f.write("\n\n# Classe para compatibilidade com o código existente\n")
                f.write("class Game(Gorillas3DWar):\n")
                f.write("    \"\"\"Classe para compatibilidade com código existente que importa Game.\n")
                f.write("    Esta classe herda todas as funcionalidades do Gorillas3DWar para manter\n")
                f.write("    compatibilidade com código que foi escrito para a versão anterior da API.\n")
                f.write("    \"\"\"\n")
                f.write("    pass\n")
            print("Classe Game adicionada ao arquivo game.py")
    
    def criar_appimage(self):
        """Cria um AppImage para distribuição no Linux"""
        print("Criando AppImage para Linux...")
        
        # Define os diretórios de trabalho
        trabalho_dir = os.path.join(self.diretorio_tmp, "AppDir")
        os.makedirs(trabalho_dir, exist_ok=True)
        os.makedirs(os.path.join(trabalho_dir, "usr", "bin"), exist_ok=True)
        os.makedirs(os.path.join(trabalho_dir, "usr", "share", "gorillas3dwar"), exist_ok=True)
        os.makedirs(os.path.join(trabalho_dir, "usr", "share", "applications"), exist_ok=True)
        os.makedirs(os.path.join(trabalho_dir, "usr", "share", "icons", "hicolor", "256x256", "apps"), exist_ok=True)
        os.makedirs(os.path.join(trabalho_dir, "usr", "lib", "dri"), exist_ok=True)
        
        # Copia os arquivos do jogo
        self._copiar_arquivos_jogo(os.path.join(trabalho_dir, "usr", "share", "gorillas3dwar"))
        
        # Cria o arquivo iniciar.py
        self._criar_arquivo_iniciar(os.path.join(trabalho_dir, "usr", "share", "gorillas3dwar"))
        
        # Cria o script wrapper
        self._criar_script_wrapper(os.path.join(trabalho_dir, "usr", "bin", "gorillas3dwar"))
        
        # Cria o arquivo .desktop
        self._criar_arquivo_desktop(os.path.join(trabalho_dir, "gorillas3dwar.desktop"))
        shutil.copy2(
            os.path.join(trabalho_dir, "gorillas3dwar.desktop"),
            os.path.join(trabalho_dir, "usr", "share", "applications", "gorillas3dwar.desktop")
        )
        
        # Copia o ícone
        self._copiar_icone(trabalho_dir)
        
        # Cria o AppRun
        self._criar_apprun(os.path.join(trabalho_dir, "AppRun"))
        
        # Baixa appimagetool se necessário
        appimagetool = self._obter_appimagetool()
        
        # Cria o AppImage
        appimage_nome = "Gorillas3DWar-x86_64.AppImage"
        subprocess.run([appimagetool, trabalho_dir, appimage_nome])
        
        # Verifica se o AppImage foi criado com sucesso
        if os.path.exists(appimage_nome):
            print(f"AppImage criado com sucesso: {appimage_nome}")
            # Torna o AppImage executável
            os.chmod(appimage_nome, 0o755)
        else:
            print("Erro ao criar o AppImage")
        
        # Limpa os arquivos temporários
        shutil.rmtree(trabalho_dir)
        
    def _copiar_arquivos_jogo(self, destino):
        """Copia os arquivos do jogo para o diretório de destino"""
        # Copia o diretório src
        shutil.copytree(self.diretorio_src, os.path.join(destino, "src"))
        
        # Copia o arquivo main.py se existir
        main_py = os.path.join(self.diretorio_base, "main.py")
        if os.path.exists(main_py):
            shutil.copy2(main_py, destino)
        
        # Copia os diretórios de recursos
        for diretorio in ["models", "textures", "sounds", "assets"]:
            dir_origem = os.path.join(self.diretorio_base, diretorio)
            if os.path.exists(dir_origem):
                shutil.copytree(dir_origem, os.path.join(destino, diretorio))
                
    def _criar_arquivo_iniciar(self, destino):
        """Cria o arquivo iniciar.py"""
        arquivo_iniciar = os.path.join(destino, "iniciar.py")
        
        with open(arquivo_iniciar, 'w', encoding='utf-8') as f:
            f.write("""#!/usr/bin/env python3
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
""")
        
        # Torna o arquivo executável
        os.chmod(arquivo_iniciar, 0o755)
        
    def _criar_script_wrapper(self, destino):
        """Cria o script wrapper para o AppImage"""
        with open(destino, 'w', encoding='utf-8') as f:
            f.write("""#!/bin/bash
# Wrapper para o Gorillas 3D War

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python 3 não está instalado. Por favor, instale-o primeiro."
    exit 1
fi

# Verifica se Panda3D está instalado
python3 -c "import panda3d" 2> /dev/null
if [ $? -ne 0 ]; then
    echo "Panda3D não está instalado. Instalando..."
    pip3 install panda3d
fi

# Executa o jogo
cd "$APPDIR/usr/share/gorillas3dwar"
python3 iniciar.py
""")
        
        # Torna o script executável
        os.chmod(destino, 0o755)
        
    def _criar_arquivo_desktop(self, destino):
        """Cria o arquivo .desktop para o AppImage"""
        with open(destino, 'w', encoding='utf-8') as f:
            f.write("""[Desktop Entry]
Name=Gorillas 3D War
Comment=Um jogo de artilharia 3D inspirado no clássico Gorillas
Exec=gorillas3dwar
Icon=gorillas3dwar
Terminal=false
Type=Application
Categories=Game;ActionGame;
""")
        
    def _copiar_icone(self, destino_base):
        """Copia o ícone para o AppImage"""
        # Verifica se existe um ícone principal
        icone_origem = os.path.join(self.diretorio_base, "textures", "icon.png")
        if os.path.exists(icone_origem):
            # Copia para o diretório de ícones do sistema
            shutil.copy2(
                icone_origem, 
                os.path.join(destino_base, "usr", "share", "icons", "hicolor", "256x256", "apps", "gorillas3dwar.png")
            )
            # Copia para o diretório raiz do AppImage
            shutil.copy2(icone_origem, os.path.join(destino_base, "gorillas3dwar.png"))
        else:
            # Verifica se existe um ícone alternativo
            icone_alt = os.path.join(self.diretorio_base, "textures", "icons", "icon_256.png")
            if os.path.exists(icone_alt):
                # Copia para o diretório de ícones do sistema
                shutil.copy2(
                    icone_alt, 
                    os.path.join(destino_base, "usr", "share", "icons", "hicolor", "256x256", "apps", "gorillas3dwar.png")
                )
                # Copia para o diretório raiz do AppImage
                shutil.copy2(icone_alt, os.path.join(destino_base, "gorillas3dwar.png"))
            else:
                print("Aviso: Nenhum ícone encontrado para o jogo.")
                
    def _criar_apprun(self, destino):
        """Cria o arquivo AppRun para o AppImage"""
        with open(destino, 'w', encoding='utf-8') as f:
            f.write("""#!/bin/bash
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
""")
        
        # Torna o arquivo executável
        os.chmod(destino, 0o755)
        
    def _obter_appimagetool(self):
        """Obtém o appimagetool, baixando-o se necessário"""
        appimagetool_path = shutil.which("appimagetool")
        if appimagetool_path:
            return appimagetool_path
            
        # Baixa o appimagetool
        appimagetool_url = "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
        appimagetool_dest = os.path.join(self.diretorio_tmp, "appimagetool")
        
        print(f"Baixando appimagetool de {appimagetool_url}...")
        subprocess.run(["wget", "-q", appimagetool_url, "-O", appimagetool_dest])
        
        # Torna o appimagetool executável
        os.chmod(appimagetool_dest, 0o755)
        
        return appimagetool_dest
    
    def criar_instalador_windows(self):
        """Cria um instalador para Windows usando NSIS"""
        if self.sistema != "windows" and not self._pode_criar_windows():
            print("A criação de instaladores Windows só é suportada no Windows ou com Wine instalado.")
            return
            
        print("Criando instalador para Windows...")
        # Implementação da criação do instalador para Windows...
        print("Criação do instalador para Windows ainda não implementada.")
        
    def _pode_criar_windows(self):
        """Verifica se é possível criar instaladores Windows em um sistema não-Windows"""
        # Verifica se Wine está instalado
        return shutil.which("wine") is not None
    
    def criar_pacote_macos(self):
        """Cria um pacote .app e .dmg para macOS"""
        if self.sistema != "darwin" and not self._pode_criar_macos():
            print("A criação de pacotes macOS só é suportada no macOS ou com ferramentas específicas.")
            return
            
        print("Criando pacote para macOS...")
        # Implementação da criação do pacote para macOS...
        print("Criação do pacote para macOS ainda não implementada.")
        
    def _pode_criar_macos(self):
        """Verifica se é possível criar pacotes macOS em um sistema não-macOS"""
        # No momento, não há suporte para criar pacotes macOS em outros sistemas
        return False
    
    def limpar_arquivos_temporarios(self):
        """Limpa todos os arquivos temporários criados durante o processo"""
        if os.path.exists(self.diretorio_tmp):
            shutil.rmtree(self.diretorio_tmp)
            print(f"Diretório temporário removido: {self.diretorio_tmp}")
            
    def distribuir(self):
        """Executa todo o processo de distribuição para todas as plataformas"""
        print("=== Iniciando distribuição do Gorillas 3D War ===")
        
        # Verifica dependências
        self.verificar_dependencias()
        
        # Corrige arquivos
        self.corrigir_arquivos()
        
        # Distribui para cada plataforma
        if self.sistema == "linux" or input("Criar AppImage para Linux? (s/n): ").lower() == "s":
            self.criar_appimage()
            
        if self.sistema == "windows" or (
            self._pode_criar_windows() and 
            input("Criar instalador para Windows? (s/n): ").lower() == "s"
        ):
            self.criar_instalador_windows()
            
        if self.sistema == "darwin" or (
            self._pode_criar_macos() and 
            input("Criar pacote para macOS? (s/n): ").lower() == "s"
        ):
            self.criar_pacote_macos()
            
        # Limpa arquivos temporários
        self.limpar_arquivos_temporarios()
        
        print("=== Distribuição concluída ===")

if __name__ == "__main__":
    distribuidor = DistribuidorGorillas()
    distribuidor.distribuir()
