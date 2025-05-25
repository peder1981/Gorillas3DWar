# Gorillas 3D War

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Patrocinar](https://img.shields.io/badge/Patrocinar-GitHub-4CAF50.svg)](https://github.com/sponsors/SEUUSUARIO)

Um jogo de artilharia 3D inspirado no clássico "Gorillas" dos anos 90, desenvolvido em Python com o motor gráfico Panda3D.

## Descrição

Gorillas 3D War é um jogo de artilharia por turnos em ambiente tridimensional onde dois jogadores controlam gorilas posicionados em prédios e arremessam bananas explosivas um no outro. 

### Características Principais

- **Gráficos 3D** com efeitos visuais avançados usando shaders
- **Física realista** usando o motor Bullet Physics para colisões e destruição
- **Sistema de clima dinâmico** que afeta a jogabilidade (chuva, neve, vento)
- **Efeitos de explosão** com partículas, luzes e detritos físicos
- **Sistema de som imersivo** com efeitos e música ambiente
- **Destruição de cenário** que permite danificar e destruir prédios
- **Otimização de desempenho** com sistema de LOD (nível de detalhe) adaptativo

## Como Jogar

### Instalação
1. Certifique-se de ter Python 3.7+ instalado
2. Instale as dependências: `pip install -r requirements.txt`
3. Execute o jogo: `python main.py`

### Controles
- **W/S**: Ajusta o ângulo de lançamento (cima/baixo)
- **A/D**: Ajusta o ângulo de lançamento (esquerda/direita)
- **Q/E**: Ajusta a força do lançamento
- **Espaço**: Lança a banana
- **R**: Reinicia o jogo (após o fim da partida)
- **C**: Alterna entre as visões de câmera
- **F**: Alterna para tela cheia
- **ESC**: Sai do jogo

## Mecânica do Jogo

- O primeiro jogador a atingir o oponente 3 vezes vence a partida
- O clima e o vento influenciam a trajetória da banana
- Destrua partes do cenário para criar novas estratégias
- Diferentes tipos de bananas com efeitos especiais

## Tecnologias Utilizadas

- **Panda3D**: Motor de renderização 3D e física
- **Bullet Physics**: Sistema de física realista para colisões e destruição
- **GLSL Shaders**: Para efeitos visuais avançados
- **Python**: Linguagem principal de desenvolvimento
- **NumPy**: Cálculos matemáticos e física

## Distribuição

### Linux (AppImage)

O jogo está disponível como AppImage para distribuições Linux:

1. Baixe o arquivo `Gorillas3DWar-x86_64.AppImage` da seção de releases
2. Torne o arquivo executável: `chmod +x Gorillas3DWar-x86_64.AppImage`
3. Execute o jogo: `./Gorillas3DWar-x86_64.AppImage`

### Windows

1. Baixe o instalador `Gorillas3DWar-Setup.exe` da seção de releases
2. Execute o instalador e siga as instruções
3. Inicie o jogo pelo ícone criado no menu iniciar ou na área de trabalho

### macOS

1. Baixe o arquivo `Gorillas3DWar.dmg` da seção de releases
2. Abra o arquivo DMG e arraste o aplicativo para a pasta Applications
3. Execute o jogo pelo Launchpad ou pela pasta Applications

## Desenvolvimento

Se quiser contribuir para o desenvolvimento do Gorillas 3D War:

```bash
# Clone o repositório
git clone https://github.com/SEUUSUARIO/Gorillas3DWar.git
cd Gorillas3DWar

# Instale as dependências
pip install -r requirements.txt

# Execute o jogo
python main.py
```

### Estrutura do Projeto

```
Gorillas3DWar/
├── src/              # Código-fonte principal do jogo
│   ├── game.py        # Classe principal do jogo
│   ├── effects.py      # Sistema de efeitos visuais
│   ├── city.py         # Gerador de cidades
│   ├── gorilla.py      # Personagens do jogo
│   └── ...
├── models/           # Modelos 3D
├── textures/         # Texturas e imagens
├── sounds/           # Efeitos sonoros e músicas
├── distribuir_gorillas.py  # Script de distribuição
├── main.py           # Ponto de entrada do jogo
└── requirements.txt  # Dependências do projeto
```

## Como Contribuir

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Patrocínio

Se você gosta deste projeto e quer apoiar seu desenvolvimento, considere se tornar um patrocinador no GitHub Sponsors. Cada contribuição é extremamente valiosa e ajuda a manter o projeto ativo!

[Patrocinar no GitHub](https://github.com/sponsors/SEUUSUARIO)

Aproveite o jogo!
