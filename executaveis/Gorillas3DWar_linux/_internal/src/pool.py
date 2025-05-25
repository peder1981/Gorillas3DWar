#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sistema de pooling de objetos para o jogo Gorillas 3D War.
Permite reutilizar objetos para melhorar o desempenho.
"""

from panda3d.core import NodePath
import weakref

class ObjectPool:
    """
    Pool genérico de objetos reutilizáveis.
    """
    
    def __init__(self, factory_func, reset_func=None, initial_size=0, max_size=100):
        """
        Inicializa o pool de objetos.
        
        Args:
            factory_func: Função que cria um novo objeto quando necessário.
            reset_func: Função que reseta um objeto para seu estado inicial antes de reutilizá-lo.
            initial_size: Número inicial de objetos a serem criados.
            max_size: Tamanho máximo do pool.
        """
        self.available = []
        self.in_use = set()
        self.factory_func = factory_func
        self.reset_func = reset_func
        self.max_size = max_size
        
        # Pré-preenche o pool com objetos iniciais
        for _ in range(initial_size):
            obj = self.factory_func()
            self.available.append(obj)
    
    def get(self):
        """
        Obtém um objeto do pool ou cria um novo se necessário.
        
        Returns:
            Um objeto do pool.
        """
        if self.available:
            obj = self.available.pop()
        else:
            obj = self.factory_func()
        
        self.in_use.add(obj)
        return obj
    
    def release(self, obj):
        """
        Devolve um objeto ao pool para reutilização.
        
        Args:
            obj: O objeto a ser devolvido ao pool.
        """
        if obj in self.in_use:
            self.in_use.remove(obj)
            
            # Reseta o objeto se necessário
            if self.reset_func:
                self.reset_func(obj)
            
            # Só adiciona de volta ao pool se não exceder o tamanho máximo
            if len(self.available) < self.max_size:
                self.available.append(obj)
            else:
                # Se for um NodePath, remove-o adequadamente
                if isinstance(obj, NodePath):
                    obj.removeNode()
    
    def release_all(self):
        """
        Devolve todos os objetos em uso ao pool.
        """
        for obj in list(self.in_use):
            self.release(obj)
    
    def clear(self):
        """
        Limpa o pool, removendo todos os objetos.
        """
        # Limpa objetos em uso
        for obj in self.in_use:
            if isinstance(obj, NodePath):
                obj.removeNode()
        
        # Limpa objetos disponíveis
        for obj in self.available:
            if isinstance(obj, NodePath):
                obj.removeNode()
        
        self.in_use.clear()
        self.available.clear()
    
    def stats(self):
        """
        Retorna estatísticas sobre o pool.
        
        Returns:
            Um dicionário com estatísticas do pool.
        """
        return {
            "available": len(self.available),
            "in_use": len(self.in_use),
            "total": len(self.available) + len(self.in_use)
        }


class ParticlePool:
    """
    Pool especializado para partículas e efeitos visuais.
    """
    
    def __init__(self, game, model_path, parent_node, initial_size=10, max_size=200):
        """
        Inicializa o pool de partículas.
        
        Args:
            game: Referência ao objeto principal do jogo.
            model_path: Caminho para o modelo 3D a ser usado como partícula.
            parent_node: Nó pai para as partículas.
            initial_size: Número inicial de partículas a serem criadas.
            max_size: Tamanho máximo do pool.
        """
        self.game = game
        self.model_path = model_path
        self.parent_node = parent_node
        
        # Função de fábrica para criar novas partículas
        def create_particle():
            particle = self.game.loader.loadModel(model_path)
            particle.reparentTo(parent_node)
            particle.hide()  # Inicia escondida
            # Configura transparência
            particle.setTransparency(1)
            return particle
        
        # Função para resetar partículas antes da reutilização
        def reset_particle(particle):
            particle.hide()
            particle.setScale(1.0)
            particle.setPos(0, 0, 0)
            particle.setHpr(0, 0, 0)
            particle.setColor(1, 1, 1, 1)
            particle.clearTexture()
            particle.setLightOff()
        
        # Cria o pool genérico
        self.pool = ObjectPool(
            factory_func=create_particle,
            reset_func=reset_particle,
            initial_size=initial_size,
            max_size=max_size
        )
    
    def get_particle(self):
        """
        Obtém uma partícula do pool.
        
        Returns:
            Uma partícula pronta para uso.
        """
        particle = self.pool.get()
        particle.show()
        return particle
    
    def release_particle(self, particle):
        """
        Devolve uma partícula ao pool.
        
        Args:
            particle: A partícula a ser devolvida.
        """
        self.pool.release(particle)
    
    def release_all(self):
        """
        Devolve todas as partículas ao pool.
        """
        self.pool.release_all()
    
    def clear(self):
        """
        Limpa o pool de partículas.
        """
        self.pool.clear()
    
    def stats(self):
        """
        Retorna estatísticas sobre o pool de partículas.
        
        Returns:
            Um dicionário com estatísticas do pool.
        """
        return self.pool.stats()
