#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sistema de shaders para efeitos visuais avançados no Gorillas 3D War.
"""

from panda3d.core import Shader, ShaderAttrib, LVector4

class ShaderManager:
    """
    Gerenciador de shaders para efeitos visuais.
    """
    
    def __init__(self, game):
        """
        Inicializa o gerenciador de shaders.
        
        Args:
            game: Referência ao objeto principal do jogo.
        """
        self.game = game
        self.shaders = {}
        self._initialize_shaders()
    
    def _initialize_shaders(self):
        """
        Inicializa os shaders disponíveis no jogo.
        """
        # Shader para efeito de explosão
        explosion_shader = self._create_explosion_shader()
        self.shaders['explosion'] = explosion_shader
        
        # Shader para efeito de onda de choque
        shockwave_shader = self._create_shockwave_shader()
        self.shaders['shockwave'] = shockwave_shader
        
        # Shader para efeito de fumaça
        smoke_shader = self._create_smoke_shader()
        self.shaders['smoke'] = smoke_shader
        
        # Shader para efeito de fogo
        fire_shader = self._create_fire_shader()
        self.shaders['fire'] = fire_shader
        
        # Shader para efeito de rastro
        trail_shader = self._create_trail_shader()
        self.shaders['trail'] = trail_shader
    
    def _create_explosion_shader(self):
        """
        Cria um shader para o efeito de explosão.
        
        Returns:
            Um objeto Shader configurado para o efeito de explosão.
        """
        # Vertex shader para explosão
        explosion_vsh = """
        #version 150
        
        // Inputs do Panda3D
        in vec4 p3d_Vertex;
        in vec2 p3d_MultiTexCoord0;
        uniform mat4 p3d_ModelViewProjectionMatrix;
        
        // Outputs para o fragment shader
        out vec2 texcoord;
        
        void main() {
            texcoord = p3d_MultiTexCoord0;
            gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
        }
        """
        
        # Fragment shader para explosão
        explosion_fsh = """
        #version 150
        
        // Inputs do vertex shader
        in vec2 texcoord;
        
        // Uniforms
        uniform sampler2D p3d_Texture0;  // Textura base
        uniform float osg_FrameTime;     // Tempo atual
        uniform float intensity;         // Intensidade do efeito
        uniform float progress;          // Progresso da explosão (0-1)
        
        // Output
        out vec4 fragColor;
        
        void main() {
            // Coordenadas centralizadas (-1 a 1)
            vec2 center = texcoord * 2.0 - 1.0;
            float dist = length(center);
            
            // Cria um anel que se expande com o tempo
            float ring = smoothstep(progress, progress + 0.1, dist) * smoothstep(dist, dist - 0.2, progress);
            
            // Adiciona distorção baseada no tempo
            float noise = sin(dist * 20.0 + osg_FrameTime * 10.0) * 0.1;
            
            // Cria gradiente de cores quentes (vermelho/amarelo/laranja)
            vec3 baseColor = mix(
                vec3(1.0, 0.3, 0.0),  // Laranja
                vec3(1.0, 0.8, 0.0),  // Amarelo
                noise + ring
            );
            
            // Calcula opacidade baseada na distância e progresso
            float alpha = (1.0 - smoothstep(0.8, 1.0, dist)) * (1.0 - progress) * intensity;
            
            // Cor final
            fragColor = vec4(baseColor, alpha);
        }
        """
        
        # Cria o shader completo
        shader = Shader.make(Shader.SL_GLSL, explosion_vsh, explosion_fsh)
        return shader
    
    def _create_shockwave_shader(self):
        """
        Cria um shader para o efeito de onda de choque.
        
        Returns:
            Um objeto Shader configurado para o efeito de onda de choque.
        """
        # Vertex shader para onda de choque
        shockwave_vsh = """
        #version 150
        
        // Inputs do Panda3D
        in vec4 p3d_Vertex;
        in vec2 p3d_MultiTexCoord0;
        uniform mat4 p3d_ModelViewProjectionMatrix;
        
        // Outputs para o fragment shader
        out vec2 texcoord;
        
        void main() {
            texcoord = p3d_MultiTexCoord0;
            gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
        }
        """
        
        # Fragment shader para onda de choque
        shockwave_fsh = """
        #version 150
        
        // Inputs do vertex shader
        in vec2 texcoord;
        
        // Uniforms
        uniform sampler2D p3d_Texture0;  // Textura base
        uniform float radius;            // Raio da onda de choque
        uniform float thickness;         // Espessura da onda
        uniform float intensity;         // Intensidade do efeito
        
        // Output
        out vec4 fragColor;
        
        void main() {
            // Coordenadas centralizadas (-1 a 1)
            vec2 center = texcoord * 2.0 - 1.0;
            float dist = length(center);
            
            // Cria um anel baseado no raio e espessura
            float ring = smoothstep(radius - thickness, radius, dist) * 
                         smoothstep(radius + thickness, radius, dist);
            
            // Cor base azulada/branca para a onda de choque
            vec3 ringColor = mix(
                vec3(0.4, 0.6, 1.0),  // Azul claro
                vec3(1.0, 1.0, 1.0),  // Branco
                ring * intensity
            );
            
            // Opacidade baseada na intensidade do anel
            float alpha = ring * intensity;
            
            // Cor final
            fragColor = vec4(ringColor, alpha);
        }
        """
        
        # Cria o shader completo
        shader = Shader.make(Shader.SL_GLSL, shockwave_vsh, shockwave_fsh)
        return shader
    
    def _create_smoke_shader(self):
        """
        Cria um shader para o efeito de fumaça.
        
        Returns:
            Um objeto Shader configurado para o efeito de fumaça.
        """
        # Vertex shader para fumaça
        smoke_vsh = """
        #version 150
        
        // Inputs do Panda3D
        in vec4 p3d_Vertex;
        in vec2 p3d_MultiTexCoord0;
        uniform mat4 p3d_ModelViewProjectionMatrix;
        
        // Outputs para o fragment shader
        out vec2 texcoord;
        
        void main() {
            texcoord = p3d_MultiTexCoord0;
            gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
        }
        """
        
        # Fragment shader para fumaça
        smoke_fsh = """
        #version 150
        
        // Inputs do vertex shader
        in vec2 texcoord;
        
        // Uniforms
        uniform sampler2D p3d_Texture0;  // Textura de ruído
        uniform float osg_FrameTime;     // Tempo atual
        uniform float density;           // Densidade da fumaça
        uniform vec4 smokeColor;         // Cor da fumaça
        
        // Output
        out vec4 fragColor;
        
        // Função de ruído para criar turbulência
        float noise(vec2 uv) {
            return texture(p3d_Texture0, uv).r;
        }
        
        void main() {
            // Adiciona movimento à fumaça
            vec2 movingUV = texcoord + vec2(0.0, osg_FrameTime * 0.1);
            
            // Várias camadas de ruído para criar turbulência
            float n1 = noise(movingUV * 1.0);
            float n2 = noise(movingUV * 2.0 + vec2(0.5, 0.0));
            float n3 = noise(movingUV * 4.0 - vec2(0.0, 0.5));
            
            // Combina as camadas de ruído
            float n = (n1 + n2 * 0.5 + n3 * 0.25) / 1.75;
            
            // Suaviza as bordas
            float edge = smoothstep(0.4, 0.6, n);
            
            // Faz a fumaça se dissipar nas bordas
            float dissipation = smoothstep(0.0, 0.6, 1.0 - length(texcoord * 2.0 - 1.0));
            
            // Aplica densidade e cor
            float alpha = edge * dissipation * density * smokeColor.a;
            vec3 color = smokeColor.rgb;
            
            // Cor final
            fragColor = vec4(color, alpha);
        }
        """
        
        # Cria o shader completo
        shader = Shader.make(Shader.SL_GLSL, smoke_vsh, smoke_fsh)
        return shader
    
    def _create_fire_shader(self):
        """
        Cria um shader para o efeito de fogo.
        
        Returns:
            Um objeto Shader configurado para o efeito de fogo.
        """
        # Vertex shader para fogo
        fire_vsh = """
        #version 150
        
        // Inputs do Panda3D
        in vec4 p3d_Vertex;
        in vec2 p3d_MultiTexCoord0;
        uniform mat4 p3d_ModelViewProjectionMatrix;
        
        // Outputs para o fragment shader
        out vec2 texcoord;
        
        void main() {
            texcoord = p3d_MultiTexCoord0;
            gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
        }
        """
        
        # Fragment shader para fogo
        fire_fsh = """
        #version 150
        
        // Inputs do vertex shader
        in vec2 texcoord;
        
        // Uniforms
        uniform sampler2D p3d_Texture0;  // Textura de ruído
        uniform float osg_FrameTime;     // Tempo atual
        uniform float intensity;         // Intensidade do fogo
        
        // Output
        out vec4 fragColor;
        
        void main() {
            // Coordenadas para criar movimento ascendente do fogo
            vec2 uv = texcoord;
            uv.y = 1.0 - uv.y;  // Inverte Y para o fogo subir
            
            // Movimento baseado no tempo
            float time = osg_FrameTime * 2.0;
            uv.y += time * 0.1;
            
            // Adiciona distorção horizontal baseada no tempo
            uv.x += sin(uv.y * 8.0 + time) * 0.05;
            
            // Obtém ruído da textura
            float noise = texture(p3d_Texture0, uv).r;
            
            // Função para criar o efeito de fogo baseado em gradiente
            float fireGradient = 1.0 - pow(texcoord.y, 2.0);
            
            // Combina ruído e gradiente para criar o formato do fogo
            float fireShape = noise * fireGradient;
            
            // Corta valores abaixo de um limiar para definir a forma do fogo
            fireShape = smoothstep(0.1, 0.8, fireShape) * intensity;
            
            // Calcula a cor baseada na altura (vermelho na base, amarelo no topo)
            vec3 fireColor = mix(
                vec3(1.0, 0.3, 0.0),  // Vermelho/laranja
                vec3(1.0, 0.8, 0.0),  // Amarelo
                fireShape * texcoord.y
            );
            
            // Adiciona brilho intenso no centro do fogo
            float glow = fireShape * (1.0 - abs(texcoord.x - 0.5) * 2.0);
            fireColor = mix(fireColor, vec3(1.0, 1.0, 0.5), glow * 0.5);
            
            // Opacidade baseada na forma do fogo
            float alpha = fireShape;
            
            // Cor final
            fragColor = vec4(fireColor, alpha);
        }
        """
        
        # Cria o shader completo
        shader = Shader.make(Shader.SL_GLSL, fire_vsh, fire_fsh)
        return shader
    
    def _create_trail_shader(self):
        """
        Cria um shader para o efeito de rastro.
        
        Returns:
            Um objeto Shader configurado para o efeito de rastro.
        """
        # Vertex shader para rastro
        trail_vsh = """
        #version 150
        
        // Inputs do Panda3D
        in vec4 p3d_Vertex;
        in vec2 p3d_MultiTexCoord0;
        uniform mat4 p3d_ModelViewProjectionMatrix;
        
        // Outputs para o fragment shader
        out vec2 texcoord;
        
        void main() {
            texcoord = p3d_MultiTexCoord0;
            gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
        }
        """
        
        # Fragment shader para rastro
        trail_fsh = """
        #version 150
        
        // Inputs do vertex shader
        in vec2 texcoord;
        
        // Uniforms
        uniform sampler2D p3d_Texture0;   // Textura base
        uniform float osg_FrameTime;      // Tempo atual
        uniform vec4 trailColor;          // Cor do rastro
        uniform float fadeSpeed;          // Velocidade de desaparecimento
        
        // Output
        out vec4 fragColor;
        
        void main() {
            // Coordenadas centralizadas (-1 a 1)
            vec2 center = texcoord * 2.0 - 1.0;
            float dist = length(center);
            
            // Cria um efeito de desaparecimento radial
            float fade = smoothstep(1.0, 0.0, dist);
            
            // Adiciona um efeito de pulso
            float pulse = sin(osg_FrameTime * 10.0 + dist * 5.0) * 0.1 + 0.9;
            
            // Calcula a cor e opacidade
            vec3 color = trailColor.rgb * pulse;
            float alpha = fade * trailColor.a;
            
            // Aplica desaparecimento baseado no tempo
            alpha *= max(0.0, 1.0 - (osg_FrameTime * fadeSpeed));
            
            // Cor final
            fragColor = vec4(color, alpha);
        }
        """
        
        # Cria o shader completo
        shader = Shader.make(Shader.SL_GLSL, trail_vsh, trail_fsh)
        return shader
    
    def apply_shader(self, node_path, shader_name, **params):
        """
        Aplica um shader a um NodePath com os parâmetros especificados.
        
        Args:
            node_path: O NodePath ao qual aplicar o shader.
            shader_name: Nome do shader a ser aplicado.
            **params: Parâmetros adicionais para o shader.
        
        Returns:
            True se o shader foi aplicado com sucesso, False caso contrário.
        """
        if shader_name not in self.shaders:
            print(f"Erro: Shader '{shader_name}' não encontrado.")
            return False
        
        # Aplica o shader ao NodePath
        shader = self.shaders[shader_name]
        node_path.setShader(shader)
        
        # Define os parâmetros do shader
        for param_name, param_value in params.items():
            if isinstance(param_value, (int, float)):
                node_path.setShaderInput(param_name, param_value)
            elif isinstance(param_value, tuple) and len(param_value) == 3:
                node_path.setShaderInput(param_name, LVector4(param_value[0], param_value[1], param_value[2], 1.0))
            elif isinstance(param_value, tuple) and len(param_value) == 4:
                node_path.setShaderInput(param_name, LVector4(*param_value))
        
        return True
    
    def remove_shader(self, node_path):
        """
        Remove um shader de um NodePath.
        
        Args:
            node_path: O NodePath do qual remover o shader.
        """
        node_path.clearShader()
