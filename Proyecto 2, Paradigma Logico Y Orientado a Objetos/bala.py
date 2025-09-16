# bala.py

import pygame
from constantes import ALTO_PANTALLA, ANCHO_PANTALLA, COLOR_BALA

class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y, direccion):
        super().__init__()
        self.image = pygame.Surface([10, 10])
        self.image.fill(COLOR_BALA)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.direccion = direccion
        self.velocidad = 10

    def update(self):
        if self.direccion == 'arriba': self.rect.y -= self.velocidad
        elif self.direccion == 'abajo': self.rect.y += self.velocidad
        elif self.direccion == 'izquierda': self.rect.x -= self.velocidad
        elif self.direccion == 'derecha': self.rect.x += self.velocidad

        if self.rect.bottom < 0 or self.rect.top > ALTO_PANTALLA or \
           self.rect.right < 0 or self.rect.left > ANCHO_PANTALLA:
            self.kill()