# tanque_enemigo.py

import pygame
import math
import threading
from tanque import Tanque
from bala import Bala
from constantes import *

class TanqueEnemigo(Tanque):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.velocidad = 2
        
        self._ultimo_disparo = 0
        self._ruta = []
        self._objetivo_actual_px = None
        self._calculando_ruta = False
        self._direccion = 'arriba'
        
        try:
            self.image_original = pygame.image.load("tanque_enemigo.png").convert_alpha()
            self.image_original = pygame.transform.scale(self.image_original, (TAMANO_TANQUE, TAMANO_TANQUE))
        except pygame.error:
            self.image_original = pygame.Surface([TAMANO_TANQUE, TAMANO_TANQUE])
            self.image_original.fill(COLOR_ENEMIGO)
        
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(topleft=(x, y))

    def solicitar_nueva_ruta(self, juego):
        if not self._calculando_ruta:
            self._calculando_ruta = True
            hilo = threading.Thread(target=self._hilo_buscar_ruta, args=(juego,), daemon=True)
            hilo.start()

    def _hilo_buscar_ruta(self, juego):
        try:
            nueva_ruta = juego.calcular_ruta_para_enemigo(self)
            if nueva_ruta:
                if len(nueva_ruta) > 1: nueva_ruta.pop(0)
                self._ruta = nueva_ruta
            else:
                self._ruta = []
        finally:
            self._calculando_ruta = False
    
    def rotar(self):
        angulo = 0
        if self._direccion == 'izquierda': angulo = 90
        elif self._direccion == 'derecha': angulo = -90
        elif self._direccion == 'abajo': angulo = 180
        centro_original = self.rect.center
        self.image = pygame.transform.rotate(self.image_original, angulo)
        self.rect = self.image.get_rect(center=centro_original)

    def update(self, jugador, todos_los_sprites, balas_enemigas, muros):
        # Movimiento
        if self._objetivo_actual_px is None and self._ruta:
            siguiente_pos = self._ruta.pop(0)
            self._objetivo_actual_px = (siguiente_pos[0] * TAMANO_REJILLA, siguiente_pos[1] * TAMANO_REJILLA)
        if self._objetivo_actual_px:
            pos_original = self.rect.topleft
            dx = self._objetivo_actual_px[0] - self.rect.x
            dy = self._objetivo_actual_px[1] - self.rect.y
            if abs(dx) > abs(dy):
                self.rect.x += self.velocidad if dx > 0 else -self.velocidad
                self._direccion = 'derecha' if dx > 0 else 'izquierda'
            elif dy != 0:
                self.rect.y += self.velocidad if dy > 0 else -self.velocidad
                self._direccion = 'abajo' if dy > 0 else 'arriba'
            self.rotar()
            if pygame.sprite.spritecollideany(self, muros):
                self.rect.topleft = pos_original
                self._objetivo_actual_px = None; self._ruta = []
            elif abs(self.rect.x - self._objetivo_actual_px[0]) < self.velocidad and abs(self.rect.y - self._objetivo_actual_px[1]) < self.velocidad:
                self.rect.topleft = self._objetivo_actual_px
                self._objetivo_actual_px = None
        ahora = pygame.time.get_ticks()
        distancia_total = math.sqrt((jugador.rect.centerx - self.rect.centerx)**2 + (jugador.rect.centery - self.rect.centery)**2)
        if distancia_total < DISTANCIA_DISPARO_ENEMIGO and ahora - self._ultimo_disparo > self.cooldown_disparo:
            self.disparar(jugador, todos_los_sprites, balas_enemigas)
            self._ultimo_disparo = ahora

    def disparar(self, jugador, todos_los_sprites, balas_enemigas):
        dist_x, dist_y = jugador.rect.centerx - self.rect.centerx, jugador.rect.centery - self.rect.centery
        direccion = self.determinar_direccion(dist_x, dist_y)
        bala_nueva = Bala(self.rect.centerx, self.rect.centery, direccion)
        todos_los_sprites.add(bala_nueva)
        balas_enemigas.add(bala_nueva)

    def determinar_direccion(self, dist_x, dist_y):
        if abs(dist_x) > abs(dist_y): return 'derecha' if dist_x > 0 else 'izquierda'
        else: return 'abajo' if dist_y > 0 else 'arriba'

class TanqueNormal(TanqueEnemigo):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.velocidad = 2
        self.cooldown_disparo = 2000

class TanqueRapido(TanqueEnemigo):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.velocidad = 4
        self.cooldown_disparo = 3000
        self.image_original.fill((180, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
        self.image = self.image_original.copy()

class TanqueTriple(TanqueEnemigo):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.velocidad = 1
        self.cooldown_disparo = 2500
        self.image_original.fill((0, 0, 180), special_flags=pygame.BLEND_RGB_ADD)
        self.image = self.image_original.copy()

    def disparar(self, jugador, todos_los_sprites, balas_enemigas):
        dist_x, dist_y = jugador.rect.centerx - self.rect.centerx, jugador.rect.centery - self.rect.centery
        direccion = self.determinar_direccion(dist_x, dist_y)
        bala_centro = Bala(self.rect.centerx, self.rect.centery, direccion)
        if direccion in ['arriba', 'abajo']:
            bala_izq = Bala(self.rect.left, self.rect.centery, direccion)
            bala_der = Bala(self.rect.right, self.rect.centery, direccion)
        else:
            bala_izq = Bala(self.rect.centerx, self.rect.top, direccion)
            bala_der = Bala(self.rect.centerx, self.rect.bottom, direccion)
        todos_los_sprites.add(bala_centro, bala_izq, bala_der)
        balas_enemigas.add(bala_centro, bala_izq, bala_der)