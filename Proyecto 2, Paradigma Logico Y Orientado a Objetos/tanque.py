# tanque.py

import pygame
from constantes import TAMANO_REJILLA

class Tanque(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, TAMANO_REJILLA, TAMANO_REJILLA)
        self.velocidad = 5 