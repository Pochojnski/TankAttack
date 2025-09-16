# tanque_jugador.py

import pygame
from tanque import Tanque
from bala import Bala
from constantes import *

class TanqueJugador(Tanque):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        self._vidas = 3
        self._direccion = 'arriba'
        
        self.velocidad = 2.5 
        
        try:
            self.image_original = pygame.image.load("tanque_jugador.png").convert_alpha()
            self.image_original = pygame.transform.scale(self.image_original, (TAMANO_TANQUE, TAMANO_TANQUE))
        except pygame.error:
            print("Advertencia: No se pudo cargar 'tanque_jugador.png'. Se usará un cuadrado verde.")
            self.image_original = pygame.Surface([TAMANO_TANQUE, TAMANO_TANQUE])
            self.image_original.fill(COLOR_JUGADOR)

        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(topleft=(x, y))

    def get_vidas(self):
        """Devuelve la cantidad de vidas actuales."""
        return self._vidas

    def get_direccion(self):
        """Devuelve la dirección actual."""
        return self._direccion

    def set_direccion(self, nueva_direccion):
        """Establece una nueva dirección y rota la imagen."""
        self._direccion = nueva_direccion
        self.rotar()

    def perder_vida(self):
        """Resta una vida."""
        self._vidas -= 1

    def rotar(self):
        angulo = 0
        if self._direccion == 'izquierda': angulo = 90
        elif self._direccion == 'derecha': angulo = -90
        elif self._direccion == 'abajo': angulo = 180
        
        centro_original = self.rect.center
        self.image = pygame.transform.rotate(self.image_original, angulo)
        self.rect = self.image.get_rect(center=centro_original)

    def disparar(self):
        bala = Bala(self.rect.centerx, self.rect.centery, self._direccion)
        return bala

    def update(self, *args, **kwargs):
        pass