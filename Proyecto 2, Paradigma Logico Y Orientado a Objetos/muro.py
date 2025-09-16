# muro.py

import pygame
from constantes import COLOR_MURO

class Muro(pygame.sprite.Sprite):
    def __init__(self, x, y, ancho, alto):
        super().__init__()
        self.image = pygame.Surface([ancho, alto])
        self.image.fill(COLOR_MURO)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y