# objetivo.py

import pygame
from constantes import TAMANO_REJILLA

class ObjetivoBase(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.vidas = 1 

    def recibir_disparo(self):
        """Resta una vida al objetivo y lo destruye si las vidas llegan a 0."""
        self.vidas -= 1
        if self.vidas <= 0:
            self.kill() 

# --- PETROLERA NORMAL (1 GOLPE) ---
class PetroleraNormal(ObjetivoBase):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.vidas = 1
        try:
            self.image = pygame.image.load("Petrolera.png").convert()
            self.image = pygame.transform.scale(self.image, (TAMANO_REJILLA, TAMANO_REJILLA))
        except pygame.error:
            self.image = pygame.Surface([TAMANO_REJILLA, TAMANO_REJILLA])
            self.image.fill((0, 0, 200)) # Color azul si la imagen falla
        
        self.rect = self.image.get_rect(topleft=(x, y))

# --- PETROLERA FUERTE (5 GOLPES) ---
class PetroleraFuerte(ObjetivoBase):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.vidas = 5
        try:
            self.image = pygame.image.load("petrolerafuerte.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (TAMANO_REJILLA, TAMANO_REJILLA))
        except pygame.error:
            self.image = pygame.Surface([TAMANO_REJILLA, TAMANO_REJILLA])
            self.image.fill((0, 100, 200)) 
        
        self.rect = self.image.get_rect(topleft=(x, y))