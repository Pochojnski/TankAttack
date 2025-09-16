# main.py

import pygame
import random
import math
import threading
from pyswip import Prolog
from constantes import *
from tanque_jugador import TanqueJugador
from tanque_enemigo import TanqueNormal, TanqueRapido, TanqueTriple
from muro import Muro
from objetivo import PetroleraNormal, PetroleraFuerte

class Juego:
    def __init__(self):
        pygame.init()
        self.prolog = Prolog()
        try:
            self.prolog.consult("pathfinding.pl")
        except Exception as e:
            print(f"ERROR: No se pudo cargar 'pathfinding.pl': {e}")
            self.game_over = True
        
        self.prolog_lock = threading.Lock()
        
        self.pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
        pygame.display.set_caption("Tank-Attack")
        self.reloj = pygame.time.Clock()
        self.game_over = False
        self.fuente_grande = pygame.font.Font(None, 74)
        self.fuente_pequena = pygame.font.Font(None, 50)
        self.fuente_vidas = pygame.font.Font(None, 36)

        self.opciones_muros = [15, 25, 40]
        self.opcion_actual_muros_idx = 1 
        self.base_cantidad_muros = self.opciones_muros[self.opcion_actual_muros_idx]
        self.boton_editar_muros = pygame.Rect(10, ALTO_PANTALLA - 60, 180, 50)

        self.estado_juego = "inicio"
        self.nivel_actual = 0
        self.contador_recalculo_ia = 0
        
        self.boton_inicio = pygame.Rect(ANCHO_PANTALLA//2 - 100, ALTO_PANTALLA//2 - 25, 200, 50)
        self.botones_nivel = [
            pygame.Rect(ANCHO_PANTALLA//2 - 100, 200, 200, 50),
            pygame.Rect(ANCHO_PANTALLA//2 - 100, 300, 200, 50),
            pygame.Rect(ANCHO_PANTALLA//2 - 100, 400, 200, 50)
        ]

        self.todos_los_sprites = pygame.sprite.Group()
        self.muros = pygame.sprite.Group()
        self.tanques_enemigos = pygame.sprite.Group()
        self.objetivos = pygame.sprite.Group()
        self.balas_jugador = pygame.sprite.Group()
        self.balas_enemigas = pygame.sprite.Group()
        
        self.tanque_jugador = TanqueJugador(ANCHO_PANTALLA // 2, ALTO_PANTALLA - 50)
        self.posicion_inicial_jugador = (ANCHO_PANTALLA // 2, ALTO_PANTALLA - 50)

    def calcular_ruta_para_enemigo(self, enemigo):
        ruta = []
        with self.prolog_lock:
            try:
                list(self.prolog.query("retractall(inicio(_))"))
                list(self.prolog.query("retractall(fin(_))"))
                list(self.prolog.query("retractall(direccion_pref(_, _))"))
                
                start_x = enemigo.rect.x // TAMANO_REJILLA
                start_y = enemigo.rect.y // TAMANO_REJILLA
                end_x = self.tanque_jugador.rect.x // TAMANO_REJILLA
                end_y = self.tanque_jugador.rect.y // TAMANO_REJILLA
                
                dx = end_x - start_x
                dy = end_y - start_y
                if abs(dx) > abs(dy):
                    dir_primaria, dir_secundaria = ('derecha' if dx > 0 else 'izquierda'), ('abajo' if dy > 0 else 'arriba')
                else:
                    dir_primaria, dir_secundaria = ('abajo' if dy > 0 else 'arriba'), ('derecha' if dx > 0 else 'izquierda')

                self.prolog.assertz(f"inicio(pos({start_x}, {start_y}))")
                self.prolog.assertz(f"fin(pos({end_x}, {end_y}))")
                self.prolog.assertz(f"direccion_pref({dir_primaria}, {dir_secundaria})")
                
                resultado = list(self.prolog.query("buscar_camino(CaminoX, CaminoY)"))
                if resultado:
                    camino_x, camino_y = resultado[0]['CaminoX'], resultado[0]['CaminoY']
                    ruta = list(zip(camino_x, camino_y))
            except Exception as e:
                print(f"Error en hilo de Prolog: {e}")
        return ruta

    def cargar_nivel(self, numero_nivel):
        self.nivel_actual = numero_nivel
        self.todos_los_sprites.empty()
        self.muros.empty()
        self.tanques_enemigos.empty()
        self.objetivos.empty()
        self.balas_jugador.empty()
        self.balas_enemigas.empty()
        
        self.tanque_jugador.rect.topleft = self.posicion_inicial_jugador
        self.tanque_jugador.vidas = 3
        self.todos_los_sprites.add(self.tanque_jugador)
        
        zonas_seguras = [self.tanque_jugador.rect.inflate(TAMANO_REJILLA, TAMANO_REJILLA)]
        obj_pos = [(150, 100), (650, 100), (400, 300)]
        enem_pos = [(150, 140), (650, 140), (400, 340)]
        
        tipos_de_tanque = [TanqueNormal, TanqueRapido, TanqueTriple]
        tipos_de_objetivo = [PetroleraNormal, PetroleraFuerte]

        
        for x, y in obj_pos:
            tipo_elegido = random.choice(tipos_de_objetivo)
            obj = tipo_elegido(x, y)
            
            self.todos_los_sprites.add(obj)
            self.objetivos.add(obj)
            zonas_seguras.append(obj.rect.inflate(TAMANO_REJILLA, TAMANO_REJILLA))
        
        for x, y in enem_pos:
            tipo_elegido = random.choice(tipos_de_tanque)
            enemigo = tipo_elegido(x, y)
            
            self.todos_los_sprites.add(enemigo)
            self.tanques_enemigos.add(enemigo)
            zonas_seguras.append(enemigo.rect.inflate(TAMANO_REJILLA, TAMANO_REJILLA))

        
        cantidad_muros = self.base_cantidad_muros * self.nivel_actual
        muros_colocados = 0
        intentos = 0
        
        while muros_colocados < cantidad_muros and intentos < 1000:
            x, y = random.randrange(0, ANCHO_PANTALLA, TAMANO_REJILLA), random.randrange(0, ALTO_PANTALLA, TAMANO_REJILLA)
            nuevo_muro_rect = pygame.Rect(x, y, TAMANO_REJILLA, TAMANO_REJILLA)
            if not any(nuevo_muro_rect.colliderect(zona) for zona in zonas_seguras) and not any(nuevo_muro_rect.colliderect(muro.rect) for muro in self.muros):
                muro = Muro(x, y, TAMANO_REJILLA, TAMANO_REJILLA)
                self.todos_los_sprites.add(muro)
                self.muros.add(muro)
                muros_colocados += 1
            intentos += 1
        
        self.estado_juego = "jugando"

    def procesar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.estado_juego == "seleccion_nivel":

                    for i, boton in enumerate(self.botones_nivel):
                        if boton.collidepoint(event.pos):
                            self.cargar_nivel(i + 1)
                            return 

                    if self.boton_editar_muros.collidepoint(event.pos):
                        self.opcion_actual_muros_idx = (self.opcion_actual_muros_idx + 1) % len(self.opciones_muros)
                        self.base_cantidad_muros = self.opciones_muros[self.opcion_actual_muros_idx]
                
                elif self.estado_juego in ["inicio", "game_over"]:
                    self.estado_juego = "seleccion_nivel"
                elif self.estado_juego == "nivel_completado":
                    self.estado_juego = "seleccion_nivel"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.estado_juego == "jugando":
                    bala_nueva = self.tanque_jugador.disparar()
                    self.todos_los_sprites.add(bala_nueva)
                    self.balas_jugador.add(bala_nueva)

    def actualizar_estado(self):
        if self.estado_juego != "jugando":
            return
            
        self.balas_jugador.update()
        self.balas_enemigas.update()
        self.tanques_enemigos.update(self.tanque_jugador, self.todos_los_sprites, self.balas_enemigas, self.muros)

        teclas = pygame.key.get_pressed()
        se_movio = False
        
        if teclas[pygame.K_a]:
            self.tanque_jugador.set_direccion('izquierda')
            self.tanque_jugador.rect.x -= self.tanque_jugador.velocidad
            se_movio = True
        elif teclas[pygame.K_d]:
            self.tanque_jugador.set_direccion('derecha')
            self.tanque_jugador.rect.x += self.tanque_jugador.velocidad
            se_movio = True
        elif teclas[pygame.K_w]:
            self.tanque_jugador.set_direccion('arriba')
            self.tanque_jugador.rect.y -= self.tanque_jugador.velocidad
            se_movio = True
        elif teclas[pygame.K_s]:
            self.tanque_jugador.set_direccion('abajo')
            self.tanque_jugador.rect.y += self.tanque_jugador.velocidad
            se_movio = True
            
        if se_movio:
            colisiones_muro = pygame.sprite.spritecollide(self.tanque_jugador, self.muros, False)
            for muro in colisiones_muro:
                direccion = self.tanque_jugador.get_direccion()
                if direccion == 'izquierda': self.tanque_jugador.rect.left = muro.rect.right
                elif direccion == 'derecha': self.tanque_jugador.rect.right = muro.rect.left
                elif direccion == 'arriba': self.tanque_jugador.rect.top = muro.rect.bottom
                elif direccion == 'abajo': self.tanque_jugador.rect.bottom = muro.rect.top

        
        self.contador_recalculo_ia += 1
        if self.contador_recalculo_ia > 60:
            self.contador_recalculo_ia = 0
            
            with self.prolog_lock:
                list(self.prolog.query("retractall(muro(_, _))"))
                list(self.prolog.query("retractall(limite_x(_))"))
                list(self.prolog.query("retractall(limite_y(_))"))
                list(self.prolog.query("retractall(profundidad_maxima(_))"))
                
                grid_x_max, grid_y_max = ANCHO_PANTALLA // TAMANO_REJILLA, ALTO_PANTALLA // TAMANO_REJILLA
                self.prolog.assertz(f"limite_x({grid_x_max})")
                self.prolog.assertz(f"limite_y({grid_y_max})")
                self.prolog.assertz("profundidad_maxima(15)")
                for muro in self.muros:
                    self.prolog.assertz(f"muro({muro.rect.x // TAMANO_REJILLA}, {muro.rect.y // TAMANO_REJILLA})")

            for enemigo in self.tanques_enemigos:
                distancia = math.sqrt((self.tanque_jugador.rect.centerx - enemigo.rect.centerx)**2 + (self.tanque_jugador.rect.centery - enemigo.rect.centery)**2)
                if distancia < 300:
                    enemigo.solicitar_nueva_ruta(self)
        
        if self.tanque_jugador.rect.left < 0: self.tanque_jugador.rect.left = 0
        if self.tanque_jugador.rect.right > ANCHO_PANTALLA: self.tanque_jugador.rect.right = ANCHO_PANTALLA
        if self.tanque_jugador.rect.top < 0: self.tanque_jugador.rect.top = 0
        if self.tanque_jugador.rect.bottom > ALTO_PANTALLA: self.tanque_jugador.rect.bottom = ALTO_PANTALLA
        

        pygame.sprite.groupcollide(self.balas_jugador, self.muros, True, False)
        pygame.sprite.groupcollide(self.balas_jugador, self.tanques_enemigos, True, True)
        pygame.sprite.groupcollide(self.balas_enemigas, self.muros, True, False)
        
        colisiones = pygame.sprite.groupcollide(self.balas_jugador, self.objetivos, True, False)
        for bala, objetivos_chocados in colisiones.items():
            for objetivo in objetivos_chocados:
                objetivo.recibir_disparo()

        if not self.objetivos and len(colisiones) > 0:
            self.estado_juego = "nivel_completado"
        
        impactos_al_jugador = pygame.sprite.spritecollide(self.tanque_jugador, self.balas_enemigas, True)
        if impactos_al_jugador:
            self.tanque_jugador.perder_vida() 
            print(f"¡Impacto! Vidas restantes: {self.tanque_jugador.get_vidas()}")
            self.tanque_jugador.rect.topleft = self.posicion_inicial_jugador
            if self.tanque_jugador.get_vidas() <= 0: 
                self.estado_juego = "game_over"

    def dibujar_elementos(self):
        self.pantalla.fill(COLOR_FONDO)
        if self.estado_juego == "inicio":
            self.dibujar_pantalla_inicio()
        elif self.estado_juego == "seleccion_nivel":
            self.dibujar_pantalla_seleccion()
        elif self.estado_juego == "jugando":
            self.todos_los_sprites.draw(self.pantalla)
            # --- CORRECCIÓN: Usar el método público para mostrar las vidas ---
            self.dibujar_texto(f"Vidas: {self.tanque_jugador.get_vidas()}", self.fuente_vidas, COLOR_NEGRO, self.pantalla, 60, 25)
        elif self.estado_juego == "nivel_completado":
            self.dibujar_pantalla_nivel_completado()
        elif self.estado_juego == "game_over":
            self.dibujar_pantalla_game_over()
        pygame.display.flip()

    def dibujar_texto(self, texto, fuente, color, superficie, x, y):
        text_obj = fuente.render(texto, True, color)
        text_rect = text_obj.get_rect()
        text_rect.center = (x, y)
        superficie.blit(text_obj, text_rect)

    def dibujar_pantalla_inicio(self):
        self.dibujar_texto("Tank-Attack", self.fuente_grande, COLOR_NEGRO, self.pantalla, ANCHO_PANTALLA//2, 150)
        pygame.draw.rect(self.pantalla, COLOR_JUGADOR, self.boton_inicio)
        self.dibujar_texto("Iniciar", self.fuente_pequena, COLOR_BLANCO, self.pantalla, self.boton_inicio.centerx, self.boton_inicio.centery)

    def dibujar_pantalla_seleccion(self):
        self.dibujar_texto("Selecciona un Nivel", self.fuente_grande, COLOR_NEGRO, self.pantalla, ANCHO_PANTALLA//2, 100)
        for i, boton in enumerate(self.botones_nivel):
            pygame.draw.rect(self.pantalla, COLOR_JUGADOR, boton)
            self.dibujar_texto(f"Nivel {i+1}", self.fuente_pequena, COLOR_BLANCO, self.pantalla, boton.centerx, boton.centery)

        pygame.draw.rect(self.pantalla, (100, 100, 100), self.boton_editar_muros)
        texto_muros = f"Muros: {self.base_cantidad_muros}"
        self.dibujar_texto(texto_muros, self.fuente_vidas, COLOR_BLANCO, self.pantalla, self.boton_editar_muros.centerx, self.boton_editar_muros.centery)

    def dibujar_pantalla_nivel_completado(self):
        self.dibujar_texto(f"¡Nivel {self.nivel_actual} Completado!", self.fuente_grande, COLOR_NEGRO, self.pantalla, ANCHO_PANTALLA//2, ALTO_PANTALLA//2 - 50)
        self.dibujar_texto("Haz clic para continuar", self.fuente_pequena, COLOR_NEGRO, self.pantalla, ANCHO_PANTALLA//2, ALTO_PANTALLA//2 + 50)

    def dibujar_pantalla_game_over(self):
        self.dibujar_texto("Game Over", self.fuente_grande, COLOR_ENEMIGO, self.pantalla, ANCHO_PANTALLA//2, ALTO_PANTALLA//2 - 50)
        self.dibujar_texto("Haz clic para volver al menú", self.fuente_pequena, COLOR_NEGRO, self.pantalla, ANCHO_PANTALLA//2, ALTO_PANTALLA//2 + 50)

    def ejecutar_bucle(self):
        while not self.game_over:
            self.procesar_eventos()
            self.actualizar_estado()
            self.dibujar_elementos()
            self.reloj.tick(FPS)
        pygame.quit()

if __name__ == '__main__':
    juego = Juego()
    juego.ejecutar_bucle()