#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gorillas 3D War - Módulo para efeitos visuais
"""
from panda3d.core import NodePath, PointLight, AmbientLight, Spotlight
from panda3d.core import LPoint3, LVector3, ColorBlendAttrib, TransparencyAttrib, VBase4
from panda3d.core import TextureStage, Texture, LineSegs
from direct.particles.ParticleEffect import ParticleEffect
import random
import math
import time

from panda3d.core import NodePath, LPoint3, LVector3, TransparencyAttrib
from panda3d.core import TextureStage, Texture, PNMImage, TextNode
from panda3d.core import AmbientLight, PointLight, DirectionalLight

# Importa os módulos de melhoria
from src.pool import ParticlePool, ObjectPool
from src.shaders import ShaderManager
from src.lod import GerenciadorLOD, QualidadeEfeitos

class EffectsSystem:
    """
    Sistema de efeitos visuais para o jogo Gorillas 3D War.
    Gerencia explosões, partículas, luzes, rastros e outros efeitos visuais com
    suporte a pooling, shaders, níveis de detalhe (LOD) e integração com física.
    """
    
    def __init__(self, game):
        """
        Inicializa o sistema de efeitos.
        
        Args:
            game: Referência ao objeto principal do jogo.
        """
        self.game = game
        
        # Cria nós para os diferentes tipos de efeitos visuais
        self.efeitos_node = self.game.render.attachNewNode("efeitos")
        self.rastros_node = self.game.render.attachNewNode("rastros")
        self.particulas_node = self.game.render.attachNewNode("particulas")
        self.fumaca_node = self.game.render.attachNewNode("fumaca")
        self.centelhas_node = self.game.render.attachNewNode("centelhas")
        self.fragmentos_node = self.game.render.attachNewNode("fragmentos")
        self.explosoes_node = self.game.render.attachNewNode("explosoes")
        
        # Ativa transparência para os nós que precisam
        self.rastros_node.setTransparency(TransparencyAttrib.MAlpha)
        self.particulas_node.setTransparency(TransparencyAttrib.MAlpha)
        self.fumaca_node.setTransparency(TransparencyAttrib.MAlpha)
        self.centelhas_node.setTransparency(TransparencyAttrib.MAlpha)
        
        # Inicializa o gerenciador de shaders
        self.shader_manager = ShaderManager(self.game)
        
        # Inicializa o gerenciador de LOD
        self.lod_manager = GerenciadorLOD(self.game, QualidadeEfeitos.ALTA)
        
        # Registra callback para ajustar os efeitos quando a qualidade mudar
        self.lod_manager.registrar_callback_mudanca_qualidade(self._ajustar_qualidade_efeitos)
        
        # Inicializa pools de objetos para reutilização
        self._inicializar_pools()
        
        # Obtém referência ao sistema de física (se disponível)
        self.sistema_fisica = getattr(self.game, 'sistema_fisica', None)
        
        # Listas para armazenar diferentes tipos de efeitos ativos
        self.explosoes = []
        self.rastros = []
        self.particulas_ativas = []
        self.fragmentos = []
        
        # Carrega texturas para efeitos
        self.texturas = self._carregar_texturas()
        
        # Estatísticas de desempenho
        self.estatisticas = {
            'num_explosoes': 0,
            'num_particulas': 0,
            'num_rastros': 0,
            'num_fragmentos': 0,
            'tempo_render': 0.0
        }
        
        # Flag para efeitos de alta qualidade
        self.usar_shaders = True
        self.usar_fisica_avancada = True
        
        # Aplica configurações iniciais baseadas no LOD
        self._aplicar_configuracoes_lod()
    
    def _inicializar_pools(self):
        """
        Inicializa os pools de objetos para reutilização.
        """
        # Pool para partículas de explosão
        self.pool_particulas_explosao = ParticlePool(
            self.game, 
            "models/misc/sphere", 
            self.particulas_node,
            initial_size=50,
            max_size=200
        )
        
        # Pool para partículas de fumaça
        self.pool_particulas_fumaca = ParticlePool(
            self.game, 
            "models/misc/plane", 
            self.fumaca_node,
            initial_size=20,
            max_size=100
        )
        
        # Pool para centelhas
        self.pool_centelhas = ParticlePool(
            self.game, 
            "models/misc/sphere", 
            self.centelhas_node,
            initial_size=30,
            max_size=150
        )
        
        # Pool para rastros
        self.pool_rastros = ParticlePool(
            self.game, 
            "models/misc/sphere", 
            self.rastros_node,
            initial_size=40,
            max_size=200
        )
        
        # Pool para luzes (função de fábrica customizada)
        def criar_luz():
            luz = PointLight('luz_pool')
            luz.setColor((1, 0.5, 0.2, 1))
            luz.setAttenuation((1, 0, 0.5))
            luz_np = self.game.render.attachNewNode(luz)
            luz_np.setPos(0, 0, 0)
            return luz_np
        
        def resetar_luz(luz_np):
            luz_np.setPos(0, 0, 0)
            luz_np.getNode().setColor((1, 0.5, 0.2, 1))
            luz_np.getNode().setAttenuation((1, 0, 0.5))
            self.game.render.clearLight(luz_np)
            
        self.pool_luzes = ObjectPool(
            factory_func=criar_luz,
            reset_func=resetar_luz,
            initial_size=5,
            max_size=20
        )
    
    def _carregar_texturas(self):
        """
        Carrega as texturas para os efeitos visuais.
        
        Returns:
            Dicionário com as texturas carregadas.
        """
        texturas = {}
        
        # Textura para fumaça
        tex_fumaca = self.game.loader.loadTexture("texturas/fumaca.png")
        if not tex_fumaca:
            # Cria uma textura de fumaça procedural se não existir
            tex_fumaca = self._criar_textura_procedural("fumaca", 128, 128)
        texturas['fumaca'] = tex_fumaca
        
        # Textura para fogo
        tex_fogo = self.game.loader.loadTexture("texturas/fogo.png")
        if not tex_fogo:
            # Cria uma textura de fogo procedural se não existir
            tex_fogo = self._criar_textura_procedural("fogo", 128, 128)
        texturas['fogo'] = tex_fogo
        
        # Textura para explosão
        tex_explosao = self.game.loader.loadTexture("texturas/explosao.png")
        if not tex_explosao:
            # Cria uma textura de explosão procedural se não existir
            tex_explosao = self._criar_textura_procedural("explosao", 128, 128)
        texturas['explosao'] = tex_explosao
        
        # Textura para onda de choque
        tex_onda = self.game.loader.loadTexture("texturas/onda_choque.png")
        if not tex_onda:
            # Cria uma textura de onda procedural se não existir
            tex_onda = self._criar_textura_procedural("onda", 64, 64)
        texturas['onda_choque'] = tex_onda
        
        return texturas
    
    def _criar_textura_procedural(self, tipo, largura, altura):
        """
        Cria uma textura procedural para quando as texturas não estão disponíveis.
        
        Args:
            tipo: Tipo de textura a criar ('fumaca', 'fogo', 'explosao', 'onda').
            largura: Largura da textura em pixels.
            altura: Altura da textura em pixels.
            
        Returns:
            Textura procedural criada.
        """
        imagem = PNMImage(largura, altura)
        imagem.addAlpha()
        
        if tipo == 'fumaca':
            # Cria uma textura de fumaça com gradiente radial
            for x in range(largura):
                for y in range(altura):
                    # Calcula distância normalizada do centro
                    dx = (x / largura) - 0.5
                    dy = (y / altura) - 0.5
                    dist = math.sqrt(dx*dx + dy*dy) * 2.0
                    
                    # Cria gradiente radial
                    valor = max(0, 1.0 - dist)
                    valor = valor * valor  # Mais concentrado no centro
                    
                    # Define cor e alpha
                    imagem.setXel(x, y, valor, valor, valor)
                    imagem.setAlpha(x, y, valor * 0.8)
        
        elif tipo == 'fogo':
            # Cria uma textura de fogo com gradiente vertical
            for x in range(largura):
                for y in range(altura):
                    # Posição normalizada
                    nx = x / largura
                    ny = y / altura
                    
                    # Adiciona ruído para parecer mais natural
                    noise = random.random() * 0.2
                    
                    # Gradiente de cores (vermelho -> amarelo)
                    r = min(1.0, 0.7 + ny * 0.3 + noise)
                    g = ny * 0.7 + noise * 0.5
                    b = noise * 0.1
                    
                    # Define cor e alpha
                    imagem.setXel(x, y, r, g, b)
                    imagem.setAlpha(x, y, (1.0 - ny) * 0.9)
        
        elif tipo == 'explosao':
            # Cria uma textura de explosão com gradiente radial
            for x in range(largura):
                for y in range(altura):
                    # Calcula distância normalizada do centro
                    dx = (x / largura) - 0.5
                    dy = (y / altura) - 0.5
                    dist = math.sqrt(dx*dx + dy*dy) * 2.0
                    
                    # Cria um anel
                    valor = max(0, 1.0 - abs(dist - 0.5) * 2.0)
                    valor = pow(valor, 0.5)  # Ajusta contraste
                    
                    # Define cor e alpha
                    r = min(1.0, valor * 1.5)
                    g = valor * 0.6
                    b = valor * 0.3
                    imagem.setXel(x, y, r, g, b)
                    imagem.setAlpha(x, y, valor)
        
        elif tipo == 'onda':
            # Cria uma textura de onda de choque (anel)
            for x in range(largura):
                for y in range(altura):
                    # Calcula distância normalizada do centro
                    dx = (x / largura) - 0.5
                    dy = (y / altura) - 0.5
                    dist = math.sqrt(dx*dx + dy*dy) * 2.0
                    
                    # Cria um anel fino
                    valor = max(0, 1.0 - abs(dist - 0.8) * 8.0)
                    
                    # Define cor e alpha
                    imagem.setXel(x, y, 1, 1, 1)
                    imagem.setAlpha(x, y, valor)
        
        # Cria a textura do Panda3D a partir da imagem
        textura = Texture()
        textura.load(imagem)
        textura.setMagfilter(Texture.FTLinear)
        textura.setMinfilter(Texture.FTLinearMipmapLinear)
        
        return textura
    
    def _aplicar_configuracoes_lod(self):
        """
        Aplica as configurações de acordo com o nível de detalhe atual.
        """
        # Obtém as configurações atuais de LOD
        config = self.lod_manager.obter_configuracoes_atuais()
        
        # Aplica as configurações
        self.usar_shaders = config['usar_shaders']
        self.max_particulas_explosao = config['max_particulas_explosao']
        self.max_particulas_fumaca = config['max_particulas_fumaca']
        self.max_fragmentos = config['max_fragmentos']
        self.duracao_efeitos = config['duracao_efeitos']
        self.max_luzes = config['max_luzes']
        self.max_rastros = config['max_rastros']
        
        # Ajusta o raio das luzes
        if hasattr(self, 'pool_luzes'):
            for luz in self.pool_luzes.in_use:
                luz.getNode().setAttenuation((1, 0, 1.0/config['raio_luz']))
    
    def _ajustar_qualidade_efeitos(self, qualidade_antiga, qualidade_nova, config):
        """
        Callback chamado quando a qualidade dos efeitos muda.
        
        Args:
            qualidade_antiga: Qualidade anterior.
            qualidade_nova: Nova qualidade.
            config: Configurações para a nova qualidade.
        """
        # Aplica novas configurações
        self.usar_shaders = config['usar_shaders']
        self.max_particulas_explosao = config['max_particulas_explosao']
        self.max_particulas_fumaca = config['max_particulas_fumaca']
        self.max_fragmentos = config['max_fragmentos']
        self.duracao_efeitos = config['duracao_efeitos']
        self.max_luzes = config['max_luzes']
        self.max_rastros = config['max_rastros']
        
        # Ajusta efeitos ativos
        self._ajustar_efeitos_ativos(config)
        
        # Log da mudança
        print(f"Qualidade de efeitos alterada: {qualidade_antiga.name} -> {qualidade_nova.name}")
    
    def _ajustar_efeitos_ativos(self, config):
        """
        Ajusta os efeitos ativos de acordo com as novas configurações.
        
        Args:
            config: Novas configurações de qualidade.
        """
        # Limita o número de partículas em explosões ativas
        for explosao in self.explosoes:
            if 'particulas' in explosao and len(explosao['particulas']) > config['max_particulas_explosao']:
                # Remove partículas excedentes
                excesso = len(explosao['particulas']) - config['max_particulas_explosao']
                for _ in range(excesso):
                    if explosao['particulas']:
                        particula = explosao['particulas'].pop()
                        particula['node'].removeNode()
            
            # Ajusta duração dos efeitos
            if explosao['duracao'] > config['duracao_efeitos']:
                tempo_restante = explosao['duracao'] - explosao['tempo']
                # Ajusta o tempo restante proporcional à nova duração
                fator = config['duracao_efeitos'] / explosao['duracao']
                explosao['duracao'] = config['duracao_efeitos']
                explosao['tempo'] = max(0, explosao['duracao'] - (tempo_restante * fator))
        
        # Limita o número de rastros
        if len(self.rastros) > config['max_rastros']:
            excesso = len(self.rastros) - config['max_rastros']
            for _ in range(excesso):
                if self.rastros:
                    rastro = self.rastros.pop(0)  # Remove os mais antigos
                    rastro['node'].removeNode()
        
        # Lista de rastros de projéteis
        self.rastros = []
        
        # Nó pai para todos os efeitos
        self.efeitos_node = NodePath("efeitos")
        self.efeitos_node.reparentTo(game.render)
        
        # Cria nós separados para diferentes tipos de efeitos
        self.explosoes_node = NodePath("explosoes")
        self.explosoes_node.reparentTo(self.efeitos_node)
        
        self.particulas_node = NodePath("particulas")
        self.particulas_node.reparentTo(self.efeitos_node)
        
        self.rastros_node = NodePath("rastros")
        self.rastros_node.reparentTo(self.efeitos_node)
        
        # Pré-configura configurações de partículas
        self.configurar_sistema_particulas()
        
    def configurar_sistema_particulas(self):
        """
        Configura o sistema de partículas para uso posterior.
        """
        # Configurações base para diferentes tipos de partículas
        self.config_particulas = {
            'explosao': self._configurar_particulas_explosao(),
            'fogo': self._configurar_particulas_fogo(),
            'fumaca': self._configurar_particulas_fumaca(),
            'centelhas': self._configurar_particulas_centelhas(),
            'poeira': self._configurar_particulas_poeira(),
            'rastro': self._configurar_particulas_rastro()
        }
    
    def _configurar_particulas_explosao(self):
        """
        Configura as partículas para explosão principal.
        """
        # Cria um novo efeito de partículas
        particulas = ParticleEffect()
        p0 = Particles('particles-explosao')
        
        # Configura o emissor, renderizador, etc.
        # Normalmente carregado de um arquivo .ptf
        
        return particulas
    
    def _configurar_particulas_fogo(self):
        """
        Configura as partículas para efeito de fogo.
        """
        particulas = ParticleEffect()
        return particulas
    
    def _configurar_particulas_fumaca(self):
        """
        Configura as partículas para efeito de fumaça.
        """
        particulas = ParticleEffect()
        return particulas
    
    def _configurar_particulas_centelhas(self):
        """
        Configura as partículas para efeito de centelhas.
        """
        particulas = ParticleEffect()
        return particulas
    
    def _configurar_particulas_poeira(self):
        """
        Configura as partículas para efeito de poeira.
        """
        particulas = ParticleEffect()
        return particulas
    
    def _configurar_particulas_rastro(self):
        """
        Configura as partículas para efeito de rastro de projétil.
        """
        particulas = ParticleEffect()
        return particulas
        
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
        try:
            onda_choque = self._criar_onda_choque(explosao_node, cor_base, raio)
            explosao['onda_choque'] = onda_choque
        except Exception as e:
            print(f"Aviso: Erro ao criar onda de choque: {e}")
            explosao['onda_choque'] = None
        
        # Cria o flash de luz inicial
        try:
            flash = self._criar_flash_explosao(explosao_node, cor_base, raio)
            explosao['flash'] = flash
        except Exception as e:
            print(f"Aviso: Erro ao criar flash de explosão: {e}")
            explosao['flash'] = None
        
        # Cria as partículas de explosão
        try:
            particulas = self._criar_particulas_explosao(explosao_node, num_particulas, raio, cor_base, duracao)
            explosao['particulas'] = particulas
        except Exception as e:
            print(f"Aviso: Erro ao criar partículas de explosão: {e}")
            particulas = []
            explosao['particulas'] = particulas
        
        # Cria centelhas
        num_centelhas = max(5, int(num_particulas * 0.3))
        centelhas = self._criar_centelhas_explosao(explosao_node, num_centelhas, raio)
        explosao['centelhas'] = centelhas
        
        # Cria fumaça
        num_nuvens_fumaca = max(3, int(num_particulas * 0.2))
        try:
            self._criar_fumaca_explosao(explosao, num_nuvens_fumaca, raio, duracao)
        except Exception as e:
            print(f"Aviso: Erro ao criar fumaça de explosão: {e}")
            explosao['fumaca'] = []
        
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
    def _criar_luzes_explosao(self, node_pai, cor_base, raio):
        """
        Cria luzes para a explosão para iluminar dinamicamente a cena.
        
        Args:
            node_pai: Nó pai para anexar as luzes.
            cor_base: Cor base da explosão.
            raio: Raio da explosão que afeta o alcance das luzes.
            
        Returns:
            Lista de luzes criadas para a explosão.
        """
        # Lista para armazenar as luzes criadas
        luzes = []
        
        try:
            # Luz principal no centro da explosão
            luz_central = PointLight('luz_explosao_central')
            luz_central.setColor(VBase4(cor_base[0], cor_base[1], cor_base[2], 1))
            luz_central.setAttenuation(LVector3(0.0, 0.0, 0.5 / raio))
            luz_central_np = node_pai.attachNewNode(luz_central)
            luz_central_np.setPos(0, 0, 0)
            
            # Define alcance com base no raio da explosão
            alcance = raio * 3.0
            luz_central.setMaxDistance(alcance)
            
            # Ativa a luz na cena
            self.game.render.setLight(luz_central_np)
            
            luzes.append({
                'node': luz_central_np,
                'light': luz_central,
                'tipo': 'central',
                'intensidade_inicial': 1.0
            })
            
            # Luz secundária com cor mais quente (tons de laranja)
            luz_sec = PointLight('luz_explosao_secundaria')
            cor_sec = VBase4(min(1.0, cor_base[0] * 1.2), 
                            min(1.0, cor_base[1] * 0.7),
                            min(0.5, cor_base[2] * 0.3), 1)
            luz_sec.setColor(cor_sec)
            luz_sec.setAttenuation(LVector3(0.0, 0.0, 1.0 / raio))
            luz_sec_np = node_pai.attachNewNode(luz_sec)
            luz_sec_np.setPos(0, 0, 0)
            
            # Define alcance menor para a luz secundária
            luz_sec.setMaxDistance(alcance * 0.6)
            
            # Ativa a luz na cena
            self.game.render.setLight(luz_sec_np)
            
            luzes.append({
                'node': luz_sec_np,
                'light': luz_sec,
                'tipo': 'secundaria',
                'intensidade_inicial': 0.8
            })
            
        except Exception as e:
            # Em caso de erro na criação de luzes, registra o problema mas não falha
            print(f"Aviso: Erro ao criar luzes para explosão: {e}")
        
        return luzes
    
    def _criar_onda_choque(self, node_pai, cor_base, raio):
        """
        Cria uma onda de choque visual para a explosão (esfera que expande).
        
        Args:
            node_pai: Nó pai para anexar a onda de choque.
            cor_base: Cor base da explosão.
            raio: Raio da explosão.
            
        Returns:
            NodePath da onda de choque criada.
        """
        # Cria uma esfera para representar a onda de choque
        onda = self.game.loader.loadModel("models/misc/sphere")
        onda.reparentTo(node_pai)
        
        # Configura a aparência da onda
        onda.setTransparency(TransparencyAttrib.MAlpha)
        
        # Define a cor inicial da onda com base na cor da explosão
        # Geralmente mais clara e transparente
        r, g, b = cor_base
        cor_onda = VBase4(
            min(1.0, r * 1.5),  # Mais claro no vermelho
            min(1.0, g * 1.5),  # Mais claro no verde
            min(1.0, b * 1.5),  # Mais claro no azul
            0.7                # Semi-transparente
        )
        onda.setColor(cor_onda)
        
        # Escala inicial muito pequena, vai crescer com o tempo
        onda.setScale(0.1)
        
        # Aplica um efeito de mistura aditiva para dar um brilho mais intenso
        onda.setAttrib(ColorBlendAttrib.make(
            ColorBlendAttrib.MAdd, 
            ColorBlendAttrib.OIncomingAlpha, 
            ColorBlendAttrib.OOne))
        
        # Se tiver shader manager, aplica shader de onda de choque
        if hasattr(self, 'shader_manager') and self.shader_manager:
            try:
                # Verifica se o método aplicar_shader existe
                if hasattr(self.shader_manager, 'aplicar_shader'):
                    self.shader_manager.aplicar_shader('onda_choque', onda)
                # Tenta outro método comum em shader managers
                elif hasattr(self.shader_manager, 'aplicar'):
                    self.shader_manager.aplicar('onda_choque', onda)
            except Exception as e:
                print(f"Aviso: Não foi possível aplicar shader à onda de choque: {e}")
        
        return onda
        
    def _criar_flash_explosao(self, node_pai, cor_base, raio):
        """
        Cria um flash de luz inicial para a explosão.
        
        Args:
            node_pai: Nó pai para anexar o flash.
            cor_base: Cor base da explosão.
            raio: Raio da explosão.
            
        Returns:
            NodePath do flash criado.
        """
        # Cria um quad para representar o flash
        flash = self.game.loader.loadModel("models/misc/plane")
        flash.reparentTo(node_pai)
        
        # Configura a aparência do flash
        flash.setTransparency(TransparencyAttrib.MAlpha)
        
        # Define a cor do flash (geralmente branco brilhante)
        r, g, b = cor_base
        cor_flash = VBase4(
            min(1.0, r * 2.0),  # Mais intenso no vermelho
            min(1.0, g * 2.0),  # Mais intenso no verde
            min(1.0, b * 2.0),  # Mais intenso no azul
            0.9                 # Quase opaco inicialmente
        )
        flash.setColor(cor_flash)
        
        # Tamanho inicial baseado no raio
        flash.setScale(raio * 1.5)
        
        # Sempre virado para a câmera
        flash.setBillboardPointEye()
        
        # Efeito de blend aditivo para brilho intenso
        flash.setAttrib(ColorBlendAttrib.make(
            ColorBlendAttrib.MAdd, 
            ColorBlendAttrib.OIncomingAlpha, 
            ColorBlendAttrib.OOne))
        
        return flash
        
    def _criar_particulas_explosao(self, node_pai, num_particulas, raio, cor_base, duracao):
        """
        Cria partículas para a explosão.
        
        Args:
            node_pai: Nó pai para anexar as partículas.
            num_particulas: Número de partículas a criar.
            raio: Raio da explosão.
            cor_base: Cor base da explosão.
            duracao: Duração da explosão em segundos.
            
        Returns:
            Lista de partículas criadas.
        """
        particulas = []
        
        # Cria fragmentos de detritos para simular a explosão
        for _ in range(num_particulas):
            # Direção aleatória em 3D
            phi = random.uniform(0, math.pi * 2)
            theta = random.uniform(0, math.pi)
            
            x = math.sin(theta) * math.cos(phi)
            y = math.sin(theta) * math.sin(phi)
            z = math.cos(theta)
            
            # Velocidade baseada no raio (maior raio = mais velocidade)
            velocidade = random.uniform(5, 15) * (raio / 2.0)
            direcao = LVector3(x, y, z)
            
            # Cria um modelo de detrito baseado na qualidade dos efeitos
            if hasattr(self, 'qualidade') and self.qualidade == 'baixa':
                # Versão simplificada para baixa qualidade
                detrito = self.game.loader.loadModel("models/misc/sphere")
            else:
                # Escolhe entre modelos básicos que sabemos que existem
                modelos = ["models/misc/cube", "models/misc/sphere"]
                try:
                    detrito = self.game.loader.loadModel(random.choice(modelos))
                except Exception as e:
                    # Fallback para modelo mais simples em caso de erro
                    print(f"Aviso: Erro ao carregar modelo para detrito: {e}")
                    detrito = self.game.loader.loadModel("models/misc/sphere")
            
            detrito.reparentTo(node_pai)
            
            # Escala aleatória pequena
            escala = random.uniform(0.1, 0.3) * (raio / 2.0)
            detrito.setScale(escala)
            
            # Cor baseada na cor da explosão com variações
            r, g, b = cor_base
            var = 0.2  # Variação de cor
            cor_particula = (
                min(1.0, r + random.uniform(-var, var)),
                min(1.0, g + random.uniform(-var, var)),
                min(1.0, b + random.uniform(-var, var))
            )
            detrito.setColor(*cor_particula, 1)
            
            # Rotação aleatória
            detrito.setHpr(
                random.uniform(0, 360),
                random.uniform(0, 360),
                random.uniform(0, 360)
            )
            
            # Velocidade de rotação aleatória
            rot_velocidade = LVector3(
                random.uniform(-180, 180),
                random.uniform(-180, 180),
                random.uniform(-180, 180)
            )
            
            # Tempo de vida aleatório
            tempo_vida = random.uniform(duracao * 0.2, duracao * 0.8)
            
            # Adiciona a partícula à lista
            particulas.append({
                'node': detrito,
                'velocidade': direcao * velocidade,
                'rotacao': rot_velocidade,
                'tempo_vida': tempo_vida,
                'tempo_inicial': tempo_vida
            })
        
        return particulas
        
    def _criar_centelhas_explosao(self, node_pai, num_centelhas, raio):
        """
        Cria centelhas brilhantes para a explosão.
        
        Args:
            node_pai: Nó pai para anexar as centelhas.
            num_centelhas: Número de centelhas a criar.
            raio: Raio da explosão.
            
        Returns:
            Lista de dicionários com informações das centelhas.
        """
        centelhas = []
        
        for _ in range(num_centelhas):
            # Direção aleatória
            phi = random.uniform(0, math.pi * 2)
            theta = random.uniform(0, math.pi)
            
            x = math.sin(theta) * math.cos(phi)
            y = math.sin(theta) * math.sin(phi)
            z = math.cos(theta)
            
            # Velocidade alta para centelhas
            velocidade = random.uniform(15, 30) * (raio / 2.0)
            direcao = LVector3(x, y, z)
            
            # Cria pequeno ponto brilhante
            centelha = self.game.loader.loadModel("models/misc/sphere")
            centelha.reparentTo(node_pai)
            
            # Tamanho pequeno
            escala = random.uniform(0.05, 0.15)
            centelha.setScale(escala)
            
            # Cor branca/amarela brilhante
            r = 1.0
            g = random.uniform(0.8, 1.0)
            b = random.uniform(0.3, 0.6)
            centelha.setColor(r, g, b, 1)
            centelha.setLightOff()
            
            centelhas.append({
                'node': centelha,
                'velocidade': direcao * velocidade,
                'tempo_vida': random.uniform(0.2, 1.0),
                'tempo_inicial': random.uniform(0.2, 1.0)
            })
        
        return centelhas
        
    def atualizar(self):
        """
        Atualiza todos os efeitos visuais ativos.
        """
        dt = self.game.taskMgr.globalClock.getDt()
        
        # Atualiza cada explosão
        self._atualizar_explosoes(dt)
        
        # Atualiza rastros de projéteis
        self._atualizar_rastros(dt)
        
    def _criar_fumaca_explosao(self, explosao, num_nuvens, raio, duracao):
        """
        Cria nuvens de fumaça para a explosão.
        
        Args:
            explosao: Dicionário com informações da explosão.
            num_nuvens: Número de nuvens de fumaça a criar.
            raio: Raio da explosão.
            duracao: Duração da explosão em segundos.
        """
        node_pai = explosao['node']
        fumaca = []
        
        # Cria várias nuvens de fumaça em posições aleatórias próximas ao centro
        for _ in range(num_nuvens):
            # Posição aleatória dentro do raio da explosão
            pos = LVector3(
                random.uniform(-raio/2, raio/2),
                random.uniform(-raio/2, raio/2),
                random.uniform(0, raio/2)  # Tende a subir
            )
            
            # Cria o sprite da fumaça
            nuvem = self.game.loader.loadModel("models/misc/plane")
            nuvem.reparentTo(node_pai)
            nuvem.setPos(pos)
            
            # Configura a aparência da fumaça
            nuvem.setTransparency(TransparencyAttrib.MAlpha)
            
            # Cor cinza com variações
            intensidade = random.uniform(0.3, 0.7)
            nuvem.setColor(intensidade, intensidade, intensidade, 0.3)  # Inicialmente semi-transparente
            
            # Escala aleatória
            escala_base = random.uniform(0.5, 1.5) * raio
            nuvem.setScale(escala_base * 0.2)  # Começa pequena e cresce
            
            # Sempre virado para a câmera
            nuvem.setBillboardPointEye()
            
            # Se tivermos texturas, aplica uma textura de fumaça
            if hasattr(self, 'texturas') and 'fumaca' in self.texturas:
                try:
                    nuvem.setTexture(self.texturas['fumaca'])
                except Exception as e:
                    print(f"Aviso: Não foi possível aplicar textura de fumaça: {e}")
            
            # Velocidade de subida lenta
            velocidade = LVector3(
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                random.uniform(1, 3)  # Tende a subir
            )
            
            # Velocidade de rotação lenta
            rot_vel = random.uniform(-20, 20)
            
            # Tempo de vida maior que a explosão para permanecer após
            tempo_vida = random.uniform(duracao * 1.2, duracao * 2.5)
            
            fumaca.append({
                'node': nuvem,
                'velocidade': velocidade,
                'rotacao': rot_vel,
                'escala_base': escala_base,
                'escala_atual': escala_base * 0.2,
                'escala_max': escala_base * 2.0,  # Tamanho máximo que a fumaça pode crescer
                'tempo_vida': tempo_vida,
                'tempo_inicial': tempo_vida,
                'alpha_inicial': 0.3
            })
        
        # Armazena a lista de fumaça na explosão
        explosao['fumaca'] = fumaca
    
    def _atualizar_explosoes(self, dt):
        """
        Atualiza todas as explosões ativas.
        
        Args:
            dt: Delta time (tempo desde o último frame).
        """
        # Atualiza cada explosão
        for explosao in list(self.explosoes):
            explosao['tempo'] += dt
            
            # Calcula o progresso normalizado da explosão (0.0 a 1.0)
            tempo_normalizado = explosao['tempo'] / explosao['duracao']
            
            # Atualiza a onda de choque (esfera que expande)
            if 'onda_choque' in explosao and explosao['onda_choque']:
                self._atualizar_onda_choque(explosao, tempo_normalizado, dt)
            
            # Atualiza o flash inicial
            if 'flash' in explosao and explosao['flash']:
                self._atualizar_flash_explosao(explosao, tempo_normalizado, dt)
            
            # Atualiza as partículas de detritos
            if 'particulas' in explosao and explosao['particulas']:
                self._atualizar_particulas_explosao(explosao, dt)
            
            # Atualiza a fumaça residual
            if 'fumaca' in explosao and explosao['fumaca']:
                self._atualizar_fumaca_explosao(explosao, dt)
            
            # Atualiza as centelhas
            if 'centelhas' in explosao and explosao['centelhas']:
                self._atualizar_centelhas_explosao(explosao, dt)
            
            # Atualiza as luzes
            if 'luzes' in explosao and explosao['luzes']:
                self._atualizar_luzes_explosao(explosao, tempo_normalizado)
            
            # Remove a explosão se duração foi excedida
            if explosao['tempo'] >= explosao['duracao']:
                self._remover_explosao(explosao)
    
    def _atualizar_onda_choque(self, explosao, tempo_normalizado, dt):
        """
        Atualiza a onda de choque da explosão.
        
        Args:
            explosao: Dicionário com informações da explosão.
            tempo_normalizado: Tempo normalizado (0.0 a 1.0).
            dt: Delta time.
        """
        onda_choque = explosao['onda_choque']
        raio = explosao['raio']
        
        if tempo_normalizado < 0.4:
            # Fase de expansão rápida
            escala = tempo_normalizado * (raio * 3.0)
            onda_choque.setScale(escala)
            
            # Ajusta a transparência (diminui com o tempo)
            alpha = max(0.0, 0.8 - (tempo_normalizado * 2.0))
            onda_choque.setAlphaScale(alpha)
        else:
            # Esconde a onda de choque após a expansão inicial
            onda_choque.hide()
    
    def _atualizar_flash_explosao(self, explosao, tempo_normalizado, dt):
        """
        Atualiza o flash inicial da explosão.
        
        Args:
            explosao: Dicionário com informações da explosão.
            tempo_normalizado: Tempo normalizado (0.0 a 1.0).
            dt: Delta time.
        """
        flash = explosao['flash']
        
        # O flash só é visível no início da explosão
        if tempo_normalizado < 0.1:
            # Define a transparência (diminui rapidamente)
            alpha = max(0.0, 0.7 - (tempo_normalizado * 7.0))
            flash.setAlphaScale(alpha)
        else:
            # Esconde o flash após o início
            flash.hide()
    
    def _atualizar_particulas_explosao(self, explosao, dt):
        """
        Atualiza as partículas da explosão.
        
        Args:
            explosao: Dicionário com informações da explosão.
            dt: Delta time.
        """
        # Atualiza cada partícula
        for particula in list(explosao['particulas']):
            # Decrementa o tempo de vida
            particula['tempo_vida'] -= dt
            
            if particula['tempo_vida'] <= 0:
                # Remove a partícula
                particula['node'].removeNode()
                explosao['particulas'].remove(particula)
            else:
                # Atualiza posição com base na velocidade
                atual_pos = particula['node'].getPos()
                
                # Adiciona gravidade e friccion para simular física
                nova_vel = particula['velocidade'] + LVector3(0, 0, -9.8 * dt)  # Gravidade
                
                # Reduz velocidade (simulando resistência do ar)
                nova_vel *= 0.98
                
                # Atualiza posição
                nova_pos = atual_pos + nova_vel * dt
                particula['node'].setPos(nova_pos)
                particula['velocidade'] = nova_vel
                
                # Atualiza rotação
                if 'rotacao' in particula:
                    h, p, r = particula['node'].getHpr()
                    rot = particula['rotacao']
                    particula['node'].setHpr(h + rot.getX() * dt, 
                                            p + rot.getY() * dt, 
                                            r + rot.getZ() * dt)
                
                # Diminui gradualmente a escala e transparência
                tempo_ratio = particula['tempo_vida'] / particula['tempo_inicial']
                
                # Escala diferente para tipos diferentes de partículas
                if 'tipo' in particula and particula['tipo'] == 'fragmento':
                    escala_final = 0.05
                else:
                    escala_final = 0.01
                    
                escala_atual = particula['node'].getScale().getX()  # Assume escala uniforme
                nova_escala = max(escala_final, escala_atual * 0.99)  # Reduz gradualmente
                particula['node'].setScale(nova_escala)
                
                # Obtém a cor atual e ajusta o alpha
                cor = particula['node'].getColor()
                particula['node'].setColor(cor[0], cor[1], cor[2], tempo_ratio)
                
                # Verifica colisão com o chão
                if nova_pos.getZ() < 0.1:
                    # Quica ou pára dependendo da velocidade
                    if abs(nova_vel.getZ()) > 1.0:
                        # Quica com perda de energia
                        particula['velocidade'].setZ(-nova_vel.getZ() * 0.4)
                        
                        # Reduz velocidade horizontal (atrito)
                        particula['velocidade'].setX(nova_vel.getX() * 0.7)
                        particula['velocidade'].setY(nova_vel.getY() * 0.7)
                        
                        # Corrige a posição (acima do chão)
                        particula['node'].setZ(0.1)
                    else:
                        # Para de quicar se a velocidade for muito baixa
                        particula['velocidade'] = LVector3(0, 0, 0)
                        particula['node'].setZ(0.1)
                        
                        # Reduz o tempo de vida mais rapidamente
                        particula['tempo_vida'] -= dt * 2.0
    
    def _atualizar_fumaca_explosao(self, explosao, dt):
        """
        Atualiza a fumaça residual da explosão.
        
        Args:
            explosao: Dicionário com informações da explosão.
            dt: Delta time.
        """
        fumaca = explosao['fumaca']
        
        # Decrementa o tempo de vida
        fumaca['tempo_vida'] -= dt
        
        if fumaca['tempo_vida'] <= 0:
            # Remove toda a fumaça
            fumaca['node'].removeNode()
            explosao['fumaca'] = None
        else:
            # Calcula a proporção de tempo restante
            tempo_ratio = fumaca['tempo_vida'] / fumaca['tempo_inicial']
            
            # Atualiza cada nuvem de fumaça
            for nuvem in fumaca['nuvens']:
                # Atualiza posição (movimento lento para cima)
                atual_pos = nuvem['node'].getPos()
                nova_pos = atual_pos + nuvem['velocidade'] * dt
                nuvem['node'].setPos(nova_pos)
                
                # Aumenta a escala gradualmente (expansão da fumaça)
                escala_atual = nuvem['escala_inicial'] * (2.0 - tempo_ratio)
                nuvem['node'].setScale(escala_atual)
                
                # Diminui a opacidade com o tempo
                alpha = nuvem['alpha_inicial'] * tempo_ratio
                nuvem['node'].setAlphaScale(alpha)
    
    def _atualizar_centelhas_explosao(self, explosao, dt):
        """
        Atualiza as centelhas da explosão.
        
        Args:
            explosao: Dicionário com informações da explosão.
            dt: Delta time.
        """
        # Atualiza cada centelha
        for centelha in list(explosao['centelhas']):
            # Decrementa o tempo de vida
            centelha['tempo_vida'] -= dt
            
            if centelha['tempo_vida'] <= 0:
                # Remove a centelha
                centelha['node'].removeNode()
                explosao['centelhas'].remove(centelha)
            else:
                # Atualiza posição
                atual_pos = centelha['node'].getPos()
                
                # Adiciona gravidade (mais leve para centelhas)
                nova_vel = centelha['velocidade'] + LVector3(0, 0, -4.9 * dt)
                
                # Atualiza posição
                nova_pos = atual_pos + nova_vel * dt
                centelha['node'].setPos(nova_pos)
                centelha['velocidade'] = nova_vel
                
                # Pisca aleatoriamente para efeito de faiscamento
                if random.random() < 0.3:
                    visivel = not centelha['node'].isHidden()
                    if visivel:
                        centelha['node'].hide()
                    else:
                        centelha['node'].show()
                
                # Diminui o tamanho gradualmente
                tempo_ratio = centelha['tempo_vida'] / centelha['tempo_inicial']
                centelha['node'].setScale(0.05 * tempo_ratio)
    
    def _atualizar_luzes_explosao(self, explosao, tempo_normalizado):
        """
        Atualiza as luzes da explosão.
        
        Args:
            explosao: Dicionário com informações da explosão.
            tempo_normalizado: Tempo normalizado (0.0 a 1.0).
        """
        # Atualiza cada luz
        for luz in explosao['luzes']:
            # Calcula intensidade da luz (diminui com o tempo)
            intensidade = max(0.0, 1.0 - (tempo_normalizado * 2.0))
            
            # Se for a primeira luz (principal)
            if luz == explosao['luzes'][0]:
                # Cor de fogo (laranja/amarelo)
                cor = (intensidade, intensidade * 0.6, intensidade * 0.2, 1)
            else:
                # Cor secundaria (mais clara)
                cor = (intensidade * 0.8, intensidade * 0.5, intensidade * 0.2, 1)
                
            # Atualiza cor da luz
            luz.getNode().setColor(cor)
            
            # Remove a luz se estiver muito fraca
            if intensidade <= 0.05:
                self.game.render.clearLight(luz)
                explosao['luzes'].remove(luz)
    
    def _remover_explosao(self, explosao):
        """
        Remove completamente uma explosão.
        
        Args:
            explosao: Dicionário com informações da explosão.
        """
        # Remove luzes
        if 'luzes' in explosao and explosao['luzes']:
            for luz in explosao['luzes']:
                self.game.render.clearLight(luz)
        
        # Remove partículas
        if 'particulas' in explosao and explosao['particulas']:
            for particula in explosao['particulas']:
                particula['node'].removeNode()
                
        # Remove centelhas
        if 'centelhas' in explosao and explosao['centelhas']:
            for centelha in explosao['centelhas']:
                centelha['node'].removeNode()
                
        # Remove fumaça
        if 'fumaca' in explosao and explosao['fumaca']:
            explosao['fumaca']['node'].removeNode()
            
        # Remove onda de choque e flash
        if 'onda_choque' in explosao and explosao['onda_choque']:
            explosao['onda_choque'].removeNode()
            
        if 'flash' in explosao and explosao['flash']:
            explosao['flash'].removeNode()
            
        # Remove o nó principal
        explosao['node'].removeNode()
        
        # Remove da lista
        self.explosoes.remove(explosao)
                
    def criar_rastro_banana(self, posicao, cor=(1, 1, 0)):
        """
        Cria um efeito de rastro para a banana.
        
        Args:
            posicao: Posição para criar o rastro.
            cor: Cor do rastro (padrão: amarelo).
        """
        # Cria uma pequena partícula que vai desaparecer
        particula = self.game.loader.loadModel("models/misc/sphere")
        particula.reparentTo(self.rastros_node)
        particula.setPos(posicao)
        particula.setScale(0.1)
        
        # Configura transparência e efeito de brilho
        particula.setTransparency(TransparencyAttrib.MAlpha)
        particula.setColor(*cor, 0.7)
        particula.setLightOff()  # Não afetado por luzes para parecer brilhante
        
        # Adiciona à lista de rastros
        self.rastros.append({
            'node': particula,
            'tempo_vida': 0.5,
            'tempo_inicial': 0.5,
            'posicao': LPoint3(*posicao),
            'escala_inicial': 0.1
        })
    
    def _atualizar_rastros(self, dt):
        """
        Atualiza os rastros dos projéteis.
        
        Args:
            dt: Delta time (tempo desde o último frame).
        """
        # Atualiza cada rastro
        for rastro in list(self.rastros):
            # Decrementa o tempo de vida
            rastro['tempo_vida'] -= dt
            
            if rastro['tempo_vida'] <= 0:
                # Remove o rastro
                rastro['node'].removeNode()
                self.rastros.remove(rastro)
            else:
                # Calcula o progresso normalizado (0.0 a 1.0)
                progresso = rastro['tempo_vida'] / rastro['tempo_inicial']
                
                # Aumenta ligeiramente a escala e diminui opacidade gradualmente
                nova_escala = rastro['escala_inicial'] * (1.0 + (1.0 - progresso) * 0.5)
                rastro['node'].setScale(nova_escala)
                
                # Ajusta a transparência
                cor = rastro['node'].getColor()
                nova_cor = (cor[0], cor[1], cor[2], progresso * 0.7)
                rastro['node'].setColor(*nova_cor)
        
    def limpar_todos_efeitos(self):
        """
        Remove todos os efeitos visuais ativos.
        """
        # Remove todas as explosões
        for explosao in list(self.explosoes):
            self._remover_explosao(explosao)
            
        # Remove todos os rastros
        for rastro in self.rastros:
            rastro['node'].removeNode()
        self.rastros = []
        
        # Limpa as listas
        self.explosoes = []
        self.rastros = []
        self.particulas_ativas = []


# Classe para compatibilidade com o código existente
class ExplosionManager(EffectsSystem):
    """Classe para compatibilidade com código existente que importa ExplosionManager.
    Esta classe herda todas as funcionalidades do EffectsSystem para manter
    compatibilidade com código que foi escrito para a versão anterior da API.
    """
    pass
