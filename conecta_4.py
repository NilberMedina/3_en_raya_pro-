import pygame
import math
import sys
import numpy as np

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.font.init()

def generar_sonido(frecuencia=440, duracion=0.1, volumen=0.3, forma="sine"):
    sample_rate = 44100
    n_samples   = int(sample_rate * duracion)
    t           = np.linspace(0, duracion, n_samples, endpoint=False)
    if forma == "sine":
        wave = np.sin(2 * np.pi * frecuencia * t)
    elif forma == "square":
        wave = np.sign(np.sin(2 * np.pi * frecuencia * t))
    elif forma == "noise":
        wave = np.random.uniform(-1, 1, n_samples)
    else:
        wave = np.sin(2 * np.pi * frecuencia * t)
    fade        = np.linspace(1.0, 0.0, n_samples)
    wave        = (wave * fade * volumen * 32767).astype(np.int16)
    wave_stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(wave_stereo)

SND_CURSOR   = generar_sonido(300,  0.05, 0.2, "square")
SND_FICHA    = generar_sonido(520,  0.12, 0.4, "sine")
SND_VICTORIA = generar_sonido(880,  0.45, 0.5, "sine")
SND_EMPATE   = generar_sonido(220,  0.35, 0.4, "square")
SND_ERROR    = generar_sonido(150,  0.08, 0.3, "square")

NEGRO      = (  0,   0,   0)
BLANCO     = (255, 255, 255)
NEON_ROSA  = (255,  20, 147)
NEON_CYAN  = (  0, 255, 255)
NEON_VERDE = (  0, 255, 128)
NEON_AMAR  = (255, 255,   0)
NEON_NARAN = (255, 140,   0)
GRIS_OSC   = ( 30,  30,  30)
GRIS_MED   = ( 60,  60,  60)
AZUL_OSC   = (  5,   5,  25)

class Base:
    def __init__(self, x, y, e):
        self.x     = x
        self.y     = y
        self.e     = e
        self.color = (255, 255, 255)
        self.alfa  = 0
    def setColor(self, color): 
        self.color = color
    def setX(self, x):
        self.x = x
    def setY(self, y):
        self.y = y
    def setXY(self, x, y):
        self.x = x; self.y = y
    def setEscala(self, e):
        self.e = e

class Disco(Base):
    def __init__(self, x, y, e):
        super().__init__(x, y, e)
        self.escala_anim = 0.0
        self.apareciendo = True

    def render(self, pantalla):
        e      = self.e
        factor = min(self.escala_anim, 1.0)
        tam    = int(e * factor)
        if tam < 2:
            return
        lienzo = pygame.Surface((e, e), pygame.SRCALPHA)
        cx, cy = e // 2, e // 2
        r      = e // 2 - 3
        # sombra
        color_sombra = tuple(max(0, c // 4) for c in self.color)
        pygame.draw.circle(lienzo, color_sombra, (cx + 2, cy + 2), r)
        # disco principal relleno
        pygame.draw.circle(lienzo, self.color, (cx, cy), r)
        # borde exterior fino
        color_borde = tuple(min(255, c + 60) for c in self.color)
        pygame.draw.circle(lienzo, color_borde, (cx, cy), r, 2)
        # brillo (arco pequeño arriba-izquierda)
        brillo    = tuple(min(255, c + 180) for c in self.color)
        rect_arco = pygame.Rect(cx - r + 6, cy - r + 6, (r - 6) * 2, (r - 6) * 2)
        pygame.draw.arc(lienzo, brillo, rect_arco, math.radians(120), math.radians(170), 2)

        if factor < 1.0:
            lienzo = pygame.transform.scale(lienzo, (tam, tam))
        rect = lienzo.get_rect(topleft=(self.x, self.y))
        pantalla.blit(lienzo, rect)

class TableroC4(Base):
    FILAS = 6
    COLS  = 7
    def __init__(self, x, y, e):
        super().__init__(x, y, e)

    def ancho(self):
        return self.COLS * self.e
    def alto(self):
        return self.FILAS * self.e
    def render(self, pantalla):
        e     = self.e
        filas = self.FILAS
        cols  = self.COLS
        w     = cols * e
        h     = filas * e
        # panel principal del tablero
        lienzo = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
        # fondo sólido del panel
        fondo = pygame.Surface((w, h), pygame.SRCALPHA)
        fondo.fill((10, 10, 60, 220))
        lienzo.blit(fondo, (2, 2))
        # huecos circulares (celdas vacías)
        color_hueco = (0, 0, 0, 0)
        r = e // 2 - 4
        for fila in range(filas):
            for col in range(cols):
                cx = 2 + col * e + e // 2
                cy = 2 + fila * e + e // 2
                pygame.draw.circle(lienzo, color_hueco, (cx, cy), r)
                # borde del hueco
                pygame.draw.circle(lienzo, self.color, (cx, cy), r, 1)
        # marco exterior
        pygame.draw.rect(lienzo, self.color, (0, 0, w + 4, h + 4), 2)
        # esquinas decorativas
        largo_esq  = int(e * 0.6)
        grosor_esq = 3
        for (ox, oy, dx, dy) in [
            (0, 0, 1, 1), (w + 3, 0, -1, 1),
            (0, h + 3, 1, -1), (w + 3, h + 3, -1, -1)
        ]:
            pygame.draw.line(lienzo, NEON_AMAR, (ox, oy), (ox + dx * largo_esq, oy), grosor_esq)
            pygame.draw.line(lienzo, NEON_AMAR, (ox, oy), (ox, oy + dy * largo_esq), grosor_esq)

        pantalla.blit(lienzo, (self.x, self.y))

class CursorC4:
    def __init__(self, columna=3):
        self.columna   = columna
        self.pulso     = 0.0
        self.inc_pulso = 0.05
    def moverIzquierda(self):
        if self.columna > 0:
            self.columna -= 1
    def moverDerecha(self, max_col=6):
        if self.columna < max_col:
            self.columna += 1
    def getColumna(self):
        return self.columna
    def update(self):
        self.pulso += self.inc_pulso
        if self.pulso > math.pi * 2:
            self.pulso -= math.pi * 2
    def render(self, pantalla, x_col, y_tablero, e, color):
        alpha_val = int(160 + 95 * math.sin(self.pulso))
        cx        = x_col + e // 1.5
        cy        = y_tablero - 14
        lienzo = pygame.Surface((e, 20), pygame.SRCALPHA)
        color_a = color + (alpha_val,)
        # triángulo apuntando hacia abajo
        pts = [(e // 2, 18), (e // 2 - 8, 4), (e // 2 + 8, 4)]
        pygame.draw.polygon(lienzo, color_a, pts)
        pantalla.blit(lienzo, (x_col, y_tablero - 20))

class ConectaCuatro:
    VACIO   = 0
    FICHA_1 = 1   
    FICHA_2 = 2   
    FILAS = 6
    COLS  = 7
    PARA_GANAR = 4
    def __init__(self):
        self.matriz        = self._nueva_matriz()
        self.turno         = self.FICHA_1
        self.ganador       = self.VACIO
        self.linea_ganadora = []
        # estadísticas 
        self.victorias_1   = 0
        self.victorias_2   = 0
        self.empates       = 0
        self.partidas      = 0

    def _nueva_matriz(self):
        return [[self.VACIO] * self.COLS for _ in range(self.FILAS)]
    def getMatriz(self):
        return self.matriz
    def getTurno(self):
        return self.turno
    def getGanador(self):
        return self.ganador
    def getLineaGanadora(self):
        return self.linea_ganadora
    def getEstadisticas(self):
        return {
            "partidas":    self.partidas,
            "victorias_1": self.victorias_1,
            "victorias_2": self.victorias_2,
            "empates":     self.empates,
        }
    def _calcular_fila(self, columna):
        for fila in range(self.FILAS - 1, -1, -1):
            if self.matriz[fila][columna] == self.VACIO:
                return fila
        return None
    def jugar(self, columna):
        if self.ganador != self.VACIO or self.hayEmpate():
            return False, None
        fila = self._calcular_fila(columna)
        if fila is None:
            return False, None      # columna llena
        self.matriz[fila][columna] = self.turno
        self.verificarGanador()

        if self.ganador != self.VACIO:
            self.partidas += 1
            if self.ganador == self.FICHA_1:
                self.victorias_1 += 1
            else:
                self.victorias_2 += 1
        elif self.hayEmpate():
            self.partidas += 1
            self.empates  += 1
        else:
            self.turno = self.FICHA_2 if self.turno == self.FICHA_1 else self.FICHA_1
        return True, fila   #  pueda animar
    # Detección de victoria
    def verificarGanador(self):
        m = self.matriz
        F = self.FILAS
        C = self.COLS
        K = self.PARA_GANAR
        direcciones = [
            (0,  1),   # horizontal
            (1,  0),   # vertical
            (1,  1),   # diagonal descendente
            (1, -1),   # diagonal ascendente
        ]
        for f in range(F):
            for c in range(C):
                celda = m[f][c]
                if celda == self.VACIO:
                    continue
                for df, dc in direcciones:
                    celdas = []
                    for k in range(K):
                        nf = f + df * k
                        nc = c + dc * k
                        if 0 <= nf < F and 0 <= nc < C and m[nf][nc] == celda:
                            celdas.append((nf, nc))
                        else:
                            break
                    if len(celdas) == K:
                        self.ganador       = celda
                        self.linea_ganadora = celdas
                        return

    def hayEmpate(self):
        if self.ganador != self.VACIO:
            return False
        for c in range(self.COLS):
            if self.matriz[0][c] == self.VACIO:
                return False
        return True

    def reiniciar(self):
        self.matriz         = self._nueva_matriz()
        self.turno          = self.FICHA_1
        self.ganador        = self.VACIO
        self.linea_ganadora = []

class EscenaConecta4:
    def __init__(self):
        self.e = 72          # tamaño de celda 
        self._inicializar_escena()

    def _inicializar_escena(self):
        e = self.e
        # tablero centrado horizontalmente
        ancho_tablero = TableroC4.COLS  * e
        alto_tablero  = TableroC4.FILAS * e
        margen_x      = (ANCHO - ancho_tablero) // 2 - 10
        margen_y      = 50

        self.tablero = TableroC4(margen_x, margen_y, e)
        self.tablero.setColor(NEON_CYAN)
        self.cursor = CursorC4(columna=3)
        self.juego  = ConectaCuatro()
        # fichas gráficas en pantalla
        self.fichas_graficas = {}
        # fuentes 
        self.fuente_grande = pygame.font.SysFont("consolas", 28, bold=True)
        self.fuente_media  = pygame.font.SysFont("consolas", 18)
        self.fuente_small  = pygame.font.SysFont("consolas", 14)
        # parpadeo línea ganadora
        self.parpadeo_timer  = 0
        self.parpadeo_estado = True
    # INPUT
    def input(self, evento):
        if evento.type != pygame.KEYDOWN:
            return
        if evento.key == pygame.K_LEFT:
            self.cursor.moverIzquierda()
            SND_CURSOR.play()
        elif evento.key == pygame.K_RIGHT:
            self.cursor.moverDerecha(TableroC4.COLS - 1)
            SND_CURSOR.play()
        elif evento.key == pygame.K_RETURN:
            col = self.cursor.getColumna()
            ok, fila = self.juego.jugar(col)
            if ok:
                SND_FICHA.play()
                # crear disco gráfico con animación de aparición
                x = self.tablero.x + col  * self.e
                y = self.tablero.y + fila * self.e
                turno_jugado = self.juego.getMatriz()[fila][col]
                disco = Disco(x, y, self.e)
                disco.setColor(NEON_ROSA if turno_jugado == ConectaCuatro.FICHA_1 else NEON_CYAN)
                disco.escala_anim = 0.01
                disco.apareciendo = True
                self.fichas_graficas[(fila, col)] = disco
                if self.juego.getGanador() != ConectaCuatro.VACIO:
                    SND_VICTORIA.play()
                elif self.juego.hayEmpate():
                    SND_EMPATE.play()
            else:
                SND_ERROR.play()
        elif evento.key == pygame.K_r:
            self.juego.reiniciar()
            self.fichas_graficas = {}
            self.cursor = CursorC4(columna=3)
            self.parpadeo_timer  = 0
            self.parpadeo_estado = True
    # UPDATE
    def update(self):
        self.cursor.update()
        # animar fichas apareciendo 
        for disco in self.fichas_graficas.values():
            if disco.apareciendo:
                disco.escala_anim += 0.08
                if disco.escala_anim >= 1.0:
                    disco.escala_anim = 1.0
                    disco.apareciendo = False
        # parpadeo línea ganadora
        if self.juego.getGanador() != ConectaCuatro.VACIO or self.juego.hayEmpate():
            self.parpadeo_timer += 1
            if self.parpadeo_timer >= 18:
                self.parpadeo_timer  = 0
                self.parpadeo_estado = not self.parpadeo_estado
    # RENDER 
    def render(self, pantalla):
        e = self.e
        # 1. Dibujar discos DEBAJO del tablero para que los huecos los encuadren
        linea_gan = self.juego.getLineaGanadora()
        for (fila, col), disco in self.fichas_graficas.items():
            en_linea = (fila, col) in linea_gan
            if en_linea:
                disco.setColor(NEON_AMAR if self.parpadeo_estado else NEON_VERDE)
            disco.render(pantalla)
        # 2. Tablero encima 
        self.tablero.render(pantalla)
        # 3. Cursor flecha
        x_col = self.tablero.x + self.cursor.getColumna() * e
        color_cur = NEON_ROSA if self.juego.getTurno() == ConectaCuatro.FICHA_1 else NEON_CYAN
        self.cursor.render(pantalla, x_col, self.tablero.y, e, color_cur)
        # 4. UI
        self._render_ui(pantalla)
        # 5. Mensaje fin de juego
        ganador = self.juego.getGanador()
        empate  = self.juego.hayEmpate()
        if ganador != ConectaCuatro.VACIO or empate:
            self._render_fin(pantalla, ganador, empate)
    def _render_ui(self, pantalla):
        e          = self.e
        ox         = self.tablero.x + 7 * e + 25
        oy         = self.tablero.y
        ganador    = self.juego.getGanador()
        empate     = self.juego.hayEmpate()
        # turno actual
        if ganador == ConectaCuatro.VACIO and not empate:
            turno   = self.juego.getTurno()
            nombre  = "J1" if turno == ConectaCuatro.FICHA_1 else "J2"
            color_t = NEON_ROSA if turno == ConectaCuatro.FICHA_1 else NEON_CYAN
            pantalla.blit(self.fuente_media.render("TURNO:", True, BLANCO),       (ox, oy))
            pantalla.blit(self.fuente_grande.render(nombre,  True, color_t),      (ox, oy + 22))
        # estadísticas
        est  = self.juego.getEstadisticas()
        oy2  = oy + 80
        pantalla.blit(self.fuente_media.render("ESTADÍSTICAS", True, NEON_AMAR), (ox, oy2))
        oy2 += 22
        items = [
            (f"J1 gana: {est['victorias_1']}", NEON_ROSA),
            (f"J2 gana: {est['victorias_2']}", NEON_CYAN),
            (f"Empate:  {est['empates']}",      NEON_VERDE),
            (f"Total:   {est['partidas']}",     BLANCO),
        ]
        for txt, col in items:
            pantalla.blit(self.fuente_small.render(txt, True, col), (ox, oy2))
            oy2 += 18
        # controles
        oy2 += 10
        controles = [
            ("←→   Columna",    GRIS_MED),
            ("ENTER Soltar",     GRIS_MED),
            ("R     Reiniciar",  GRIS_MED),
        ]
        for txt, col in controles:
            pantalla.blit(self.fuente_small.render(txt, True, col), (ox, oy2))
            oy2 += 16
    def _render_fin(self, pantalla, ganador, empate):
        overlay = pygame.Surface((280, 100), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        ox = (ANCHO - 280) // 2
        oy = self.tablero.y + TableroC4.FILAS * self.e + 14
        pantalla.blit(overlay, (ox, oy))
        if ganador != ConectaCuatro.VACIO:
            nombre  = "Jugador 1" if ganador == ConectaCuatro.FICHA_1 else "Jugador 2"
            color_g = NEON_ROSA   if ganador == ConectaCuatro.FICHA_1 else NEON_CYAN
            s1 = self.fuente_grande.render(f"¡Ganó {nombre}!", True, color_g)
        else:
            s1 = self.fuente_grande.render("¡EMPATE!", True, NEON_NARAN)
        pantalla.blit(s1, (ox + 10, oy + 8))
        s2 = self.fuente_media.render("Presiona R para reiniciar", True, BLANCO)
        pantalla.blit(s2, (ox + 10, oy + 50))
#  GAME LOOP  
ANCHO = 800
ALTO  = 580
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Conecta 4")
clock  = pygame.time.Clock()
escena = EscenaConecta4()
# fondo degradado 
fondo = pygame.Surface((ANCHO, ALTO))
for y in range(ALTO):
    v = int(5 + 20 * (y / ALTO))
    fondo.fill((0, 0, v), pygame.Rect(0, y, ANCHO, 1))

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        escena.input(evento)
    escena.update()
    pantalla.blit(fondo, (0, 0))
    escena.render(pantalla)
    pygame.display.flip()
    clock.tick(60)