import pygame
import math
import sys
import numpy as np

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.font.init()

def generar_sonido(frecuencia=440, duracion=0.1, volumen=0.3, forma="sine"):
    sample_rate = 44100
    n_samples = int(sample_rate * duracion)
    t = np.linspace(0, duracion, n_samples, endpoint=False)
    if forma == "sine":
        wave = np.sin(2 * np.pi * frecuencia * t)
    elif forma == "square":
        wave = np.sign(np.sin(2 * np.pi * frecuencia * t))
    elif forma == "noise":
        wave = np.random.uniform(-1, 1, n_samples)
    else:
        wave = np.sin(2 * np.pi * frecuencia * t)
    # fade out
    fade = np.linspace(1.0, 0.0, n_samples)
    wave = (wave * fade * volumen * 32767).astype(np.int16)
    wave_stereo = np.column_stack((wave, wave))  # mono → estéreo
    sound = pygame.sndarray.make_sound(wave_stereo)
    return sound

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
        self.x = x
        self.y = y
        self.e = e
        self.color = (255, 255, 255)
        self.alfa = 0
    def setColor(self, color):
        self.color = color
    def setX(self, x):
        self.x = x  
    def setY(self, y):
        self.y = y
    def setXY(self, x, y):
        self.x = x
        self.y = y
    def setEscala(self, e):
        self.e = e

class X(Base):
    def __init__(self, x, y, e):
        super().__init__(x, y, e)
        self.escala_anim = 0.0      # animación de aparición 0→1
        self.apareciendo = True

    def render(self, pantalla):
        e = self.e
        factor = min(self.escala_anim, 1.0)
        tam = int(3 * e * factor)
        if tam < 2:
            return

        lienzo = pygame.Surface((3*e, 3*e), pygame.SRCALPHA)
        margen = int(e * 0.25)
        # sombra / borde (color más oscuro, desplazado)
        color_sombra = tuple(max(0, c//4) for c in self.color)
        pygame.draw.line(lienzo, color_sombra,(margen+2, margen+2), (3*e-margen+2, 3*e-margen+2), 5)
        pygame.draw.line(lienzo, color_sombra,(3*e-margen+2, margen+2), (margen+2, 3*e-margen+2), 5)

        # línea principal
        pygame.draw.line(lienzo, self.color,(margen, margen), (3*e-margen, 3*e-margen), 4)
        pygame.draw.line(lienzo, self.color,(3*e-margen, margen), (margen, 3*e-margen), 4)

        # brillo central (línea fina blanca encima)
        brillo = (
            min(255, self.color[0]+180),
            min(255, self.color[1]+180),
            min(255, self.color[2]+180),
        )
        pygame.draw.line(lienzo, brillo,(margen+4, margen+4), (3*e-margen-4, 3*e-margen-4), 1)
        pygame.draw.line(lienzo, brillo,(3*e-margen-4, margen+4), (margen+4, 3*e-margen-4), 1) 
        # escalar si está apareciendo
        if factor < 1.0:
            lienzo = pygame.transform.scale(lienzo, (tam, tam))
 
        rot = pygame.transform.rotate(lienzo, self.alfa)
        rect = rot.get_rect(topleft=(self.x, self.y))
        pantalla.blit(rot, rect)

class O(Base):
    def __init__(self, x, y, e):
        super().__init__(x, y, e)
        self.escala_anim = 0.0
        self.apareciendo = True

    def render(self, pantalla):
        e = self.e
        factor = min(self.escala_anim, 1.0)
        tam = int(3 * e * factor)
        if tam < 2:
            return
        lienzo = pygame.Surface((3*e, 3*e), pygame.SRCALPHA)
        cx, cy = int(3*e/2), int(3*e/2)
        r_ext = int(3*e/2) - 2
        r_int = int(3*e/2) - int(e*0.35)
        # sombra exterior
        color_sombra = tuple(max(0, c//4) for c in self.color)
        pygame.draw.circle(lienzo, color_sombra, (cx+2, cy+2), r_ext, 4)
        # círculo exterior
        pygame.draw.circle(lienzo, self.color, (cx, cy), r_ext, 4)
        # círculo interior (más tenue)
        color_int = tuple(max(0, c//2) for c in self.color)
        pygame.draw.circle(lienzo, color_int, (cx, cy), r_int, 2)
        # brillo (arco pequeño en la parte superior izquierda)
        brillo = (
            min(255, self.color[0]+180),
            min(255, self.color[1]+180),
            min(255, self.color[2]+180),
        )
        rect_arco = pygame.Rect(cx - r_ext + 4, cy - r_ext + 4,(r_ext-4)*2, (r_ext-4)*2)
        pygame.draw.arc(lienzo, brillo, rect_arco,math.radians(120), math.radians(160), 2)
        if factor < 1.0:
            lienzo = pygame.transform.scale(lienzo, (tam, tam))
        rot = pygame.transform.rotate(lienzo, self.alfa)
        rect = rot.get_rect(topleft=(self.x, self.y))
        pantalla.blit(rot, rect)

class Tablero(Base):
    def __init__(self, x, y, e, tam=3):
        super().__init__(x, y, e)
        self.tam = tam          # 3 → tablero 3×3, 4 → 4×4
    def render(self, pantalla):
        e = self.e
        n = self.tam
        total = n * 3 * e
        lienzo = pygame.Surface((total + 4, total + 4), pygame.SRCALPHA)
        # fondo semi-transparente
        fondo = pygame.Surface((total, total), pygame.SRCALPHA)
        fondo.fill((10, 10, 40, 180))
        lienzo.blit(fondo, (2, 2))
        # líneas interiores del tablero
        for i in range(1, n):
            # verticales
            pygame.draw.line(lienzo, self.color,
                             (i * 3 * e + 2, 2), (i * 3 * e + 2, total + 2), 2)
            # horizontales
            pygame.draw.line(lienzo, self.color,
                             (2, i * 3 * e + 2), (total + 2, i * 3 * e + 2), 2)
        # brillo suave en líneas (segunda pasada más fina)
        brillo = (
            min(255, self.color[0]+100),
            min(255, self.color[1]+100),
            min(255, self.color[2]+100),
        )
        for i in range(1, n):
            pygame.draw.line(lienzo, brillo,
                             (i * 3 * e + 2, 2), (i * 3 * e + 2, total + 2), 1)
            pygame.draw.line(lienzo, brillo,
                             (2, i * 3 * e + 2), (total + 2, i * 3 * e + 2), 1)
        # marco exterior
        pygame.draw.rect(lienzo, self.color, (0, 0, total + 4, total + 4), 2)
        # esquinas decorativas
        largo_esq = int(e * 0.8)
        grosor_esq = 3
        for (ox, oy, dx, dy) in [
            (0, 0, 1, 1), (total+3, 0, -1, 1),
            (0, total+3, 1, -1), (total+3, total+3, -1, -1)
        ]:
            pygame.draw.line(lienzo, NEON_AMAR,(ox, oy), (ox + dx*largo_esq, oy), grosor_esq)
            pygame.draw.line(lienzo, NEON_AMAR,(ox, oy), (ox, oy + dy*largo_esq), grosor_esq)
            
        rot = pygame.transform.rotate(lienzo, self.alfa)
        rect = rot.get_rect(topleft=(self.x, self.y))
        pantalla.blit(rot, rect)

class Cursor:
    def __init__(self, fila, columna):
        self.fila = fila
        self.columna = columna
        self.pulso = 0.0
        self.inc_pulso = 0.05
    def moverArriba(self):
        if self.fila > 0:
            self.fila -= 1
    def moverAbajo(self, max_fil=2):
        if self.fila < max_fil:
            self.fila += 1
    def moverIzquierda(self):
        if self.columna > 0:
            self.columna -= 1
    def moverDerecha(self, max_col=2):
        if self.columna < max_col:
            self.columna += 1
    def getFila(self):
        return self.fila
    def getColumna(self):
        return self.columna
    def getPosicion(self):
        return (self.fila, self.columna)
    def update(self):
        self.pulso += self.inc_pulso
        if self.pulso > math.pi * 2:
            self.pulso -= math.pi * 2
    def render(self, pantalla, x, y, e, color):
        # efecto pulsante: varía el alpha y el grosor
        alpha_val = int(160 + 95 * math.sin(self.pulso))
        grosor = 2 if math.sin(self.pulso) > 0 else 1
        lienzo = pygame.Surface((3*e, 3*e), pygame.SRCALPHA)
        color_alpha = color + (alpha_val,)
        margen = e // 2
        pygame.draw.rect(lienzo, color_alpha,(margen, margen, 2*e, 2*e), grosor)
        # esquinitas decorativas
        largo = e // 3
        for (cx, cy, sx, sy) in [
            (margen, margen, 1, 1),
            (margen + 2*e, margen, -1, 1),
            (margen, margen + 2*e, 1, -1),
            (margen + 2*e, margen + 2*e, -1, -1),
        ]:
            pygame.draw.line(lienzo, color_alpha,(cx, cy), (cx + sx*largo, cy), grosor+1)
            pygame.draw.line(lienzo, color_alpha,(cx, cy), (cx, cy + sy*largo), grosor+1)
        pantalla.blit(lienzo, (x, y))
class TresEnRaya:
    VACIO  = 0
    FICHA_X = 1
    FICHA_O = 2
    def __init__(self, tam=3, fichas_para_ganar=3):
        self.tam = tam
        self.fichas_para_ganar = fichas_para_ganar
        self.matriz = self._nueva_matriz()
        self.turno = self.FICHA_X
        self.ganador = self.VACIO
        self.linea_ganadora = []     # lista de (fila, col) que forman el trío
        # estadísticas persistentes
        self.victorias_x = 0
        self.victorias_o = 0
        self.empates = 0
        self.partidas = 0
    def _nueva_matriz(self):
        return [[self.VACIO]*self.tam for _ in range(self.tam)]
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
            "partidas": self.partidas,
            "victorias_x": self.victorias_x,
            "victorias_o": self.victorias_o,
            "empates": self.empates,
        }
    def jugar(self, fila, columna):
        if self.ganador != self.VACIO:
            return False
        if self.hayEmpate():
            return False
        if self.matriz[fila][columna] != self.VACIO:
            return False
        self.matriz[fila][columna] = self.turno
        self.verificarGanador()
        if self.ganador != self.VACIO:
            self.partidas += 1
            if self.ganador == self.FICHA_X:
                self.victorias_x += 1
            else:
                self.victorias_o += 1
        elif self.hayEmpate():
            self.partidas += 1
            self.empates += 1
        else:
            self.turno = self.FICHA_O if self.turno == self.FICHA_X else self.FICHA_X
        return True
    def verificarGanador(self):
        m = self.matriz
        n = self.tam
        k = self.fichas_para_ganar
        # filas
        for f in range(n):
            for c in range(n - k + 1):
                celda = m[f][c]
                if celda != self.VACIO and all(m[f][c+i] == celda for i in range(k)):
                    self.ganador = celda
                    self.linea_ganadora = [(f, c+i) for i in range(k)]
                    return
        # columnas
        for c in range(n):
            for f in range(n - k + 1):
                celda = m[f][c]
                if celda != self.VACIO and all(m[f+i][c] == celda for i in range(k)):
                    self.ganador = celda
                    self.linea_ganadora = [(f+i, c) for i in range(k)]
                    return
        # diagonal principal
        for f in range(n - k + 1):
            for c in range(n - k + 1):
                celda = m[f][c]
                if celda != self.VACIO and all(m[f+i][c+i] == celda for i in range(k)):
                    self.ganador = celda
                    self.linea_ganadora = [(f+i, c+i) for i in range(k)]
                    return
        # diagonal inversa
        for f in range(n - k + 1):
            for c in range(k - 1, n):
                celda = m[f][c]
                if celda != self.VACIO and all(m[f+i][c-i] == celda for i in range(k)):
                    self.ganador = celda
                    self.linea_ganadora = [(f+i, c-i) for i in range(k)]
                    return 
    def hayEmpate(self):
        if self.ganador != self.VACIO:
            return False
        for fila in self.matriz:
            for casilla in fila:
                if casilla == self.VACIO:
                    return False
        return True
    def reiniciar(self):
        self.matriz = self._nueva_matriz()
        self.turno = self.FICHA_X
        self.ganador = self.VACIO
        self.linea_ganadora = []

class EscenaTresEnRaya:
    def __init__(self, tam_tablero=3):
        self.e = 28
        self.tam_tablero = tam_tablero
        self._inicializar_escena()

    def _inicializar_escena(self):
        e = self.e
        n = self.tam_tablero
        k = 3 if n == 3 else 4   # fichas para ganar
        self.tablero = Tablero(30, 60, e, n)
        self.tablero.setColor(NEON_CYAN)
        self.cursor = Cursor(n//2, n//2)
        self.juego = TresEnRaya(n, k)
        # fichas gráficas en pantalla: guardan escala_anim para aparición
        self.fichas_graficas = {}   # (fila, col) → instancia X u O
        # indicadores de turno
        self.xTurno = X(420, 70, e)
        self.xTurno.setColor(NEON_ROSA)
        self.xTurno.escala_anim = 1.0
        self.xTurno.apareciendo = False

        self.oTurno = O(500, 70, e)
        self.oTurno.setColor(NEON_CYAN)
        self.oTurno.escala_anim = 1.0
        self.oTurno.apareciendo = False
        self.inc_turno = 0.5
        # parpadeo línea ganadora
        self.parpadeo_timer = 0
        self.parpadeo_estado = True
        # mensaje fin de juego
        self.fuente_grande = pygame.font.SysFont("consolas", 32, bold=True)
        self.fuente_media  = pygame.font.SysFont("consolas", 20)
        self.fuente_small  = pygame.font.SysFont("consolas", 16)
 
    # INPUT 
    def input(self, evento):
        if evento.type != pygame.KEYDOWN:
            return
        n = self.tam_tablero - 1
 
        if evento.key == pygame.K_UP:
            self.cursor.moverArriba()
            SND_CURSOR.play() 
        elif evento.key == pygame.K_DOWN:
            self.cursor.moverAbajo(n)
            SND_CURSOR.play()
        elif evento.key == pygame.K_LEFT:
            self.cursor.moverIzquierda()
            SND_CURSOR.play()
        elif evento.key == pygame.K_RIGHT:
            self.cursor.moverDerecha(n)
            SND_CURSOR.play()
        elif evento.key == pygame.K_RETURN:
            fila = self.cursor.getFila()
            col  = self.cursor.getColumna()
            ok   = self.juego.jugar(fila, col)
            if ok:
                SND_FICHA.play()
                # crear ficha gráfica con animación de aparición
                x = self.tablero.x + col * 3 * self.e
                y = self.tablero.y + fila * 3 * self.e
                turno_jugado = self.juego.getMatriz()[fila][col]
                if turno_jugado == TresEnRaya.FICHA_X:
                    f = X(x, y, self.e)
                    f.setColor(NEON_ROSA)
                else:
                    f = O(x, y, self.e)
                    f.setColor(NEON_CYAN)
                f.escala_anim = 0.01
                f.apareciendo = True
                self.fichas_graficas[(fila, col)] = f

                if self.juego.getGanador() != TresEnRaya.VACIO:
                    SND_VICTORIA.play()
                elif self.juego.hayEmpate():
                    SND_EMPATE.play()
            else:
                SND_ERROR.play()

        elif evento.key == pygame.K_r:
            self.juego.reiniciar()
            self.fichas_graficas = {}
            self.cursor = Cursor(self.tam_tablero//2, self.tam_tablero//2)
            self.parpadeo_timer = 0
            self.parpadeo_estado = True

        elif evento.key == pygame.K_TAB:
            # alternar entre tablero 3×3 y 4×4
            est = self.juego.getEstadisticas()
            nuevo_tam = 4 if self.tam_tablero == 3 else 3
            self.tam_tablero = nuevo_tam
            self._inicializar_escena()
            # restaurar estadísticas
            self.juego.victorias_x = est["victorias_x"]
            self.juego.victorias_o = est["victorias_o"]
            self.juego.empates     = est["empates"]
            self.juego.partidas    = est["partidas"]

    # UPDATE 
    def update(self):
        self.cursor.update()
        # animar fichas que acaban de aparecer
        for ficha in self.fichas_graficas.values():
            if ficha.apareciendo:
                ficha.escala_anim += 0.07
                if ficha.escala_anim >= 1.0:
                    ficha.escala_anim = 1.0
                    ficha.apareciendo = False 
        ganador = self.juego.getGanador()
        empate  = self.juego.hayEmpate()

        if ganador != TresEnRaya.VACIO or empate:
            # parpadeo de fichas ganadoras
            self.parpadeo_timer += 1
            if self.parpadeo_timer >= 18:
                self.parpadeo_timer = 0
                self.parpadeo_estado = not self.parpadeo_estado
            return 
        # animación indicadores de turno (oscilan)
        turno = self.juego.getTurno()
        if turno == TresEnRaya.FICHA_X:
            self.xTurno.e += self.inc_turno
            if self.xTurno.e >= self.e * 0.75 or self.xTurno.e <= self.e * 0.4:
                self.inc_turno = -self.inc_turno
            self.xTurno.alfa += 1.2
        else:
            self.oTurno.e += self.inc_turno
            if self.oTurno.e >= self.e * 0.75 or self.oTurno.e <= self.e * 0.4:
                self.inc_turno = -self.inc_turno

    # RENDER 
    def render(self, pantalla):
        n   = self.tam_tablero
        e   = self.e
        # tablero
        self.tablero.render(pantalla)
        # cursor (color según turno)
        cx = self.tablero.x + self.cursor.getColumna() * 3 * e
        cy = self.tablero.y + self.cursor.getFila()    * 3 * e
        color_cursor = NEON_ROSA if self.juego.getTurno() == TresEnRaya.FICHA_X else NEON_CYAN
        self.cursor.render(pantalla, cx, cy, e, color_cursor)
        # fichas en el tablero
        linea_gan = self.juego.getLineaGanadora()
        for (fila, col), ficha in self.fichas_graficas.items():
            en_linea = (fila, col) in linea_gan
            if en_linea:
                # parpadeo: alternar entre color normal y amarillo brillante
                if self.parpadeo_estado:
                    ficha.setColor(NEON_AMAR)
                else:
                    ficha.setColor(NEON_VERDE)
            ficha.render(pantalla)
        # indicadores de turno
        ganador = self.juego.getGanador()
        empate  = self.juego.hayEmpate()
        #UI lateral 
        self._render_ui(pantalla)
        # Mensaje fin de juego 
        if ganador != TresEnRaya.VACIO or empate:
            self._render_fin(pantalla, ganador, empate)
 
    def _render_ui(self, pantalla):
        e   = self.e
        n   = self.tam_tablero
        ancho_tablero = n * 3 * e
        ox  = self.tablero.x + ancho_tablero + 25
        oy  = self.tablero.y 
        # turno actual
        turno = self.juego.getTurno()
        ganador = self.juego.getGanador()
        empate  = self.juego.hayEmpate()

        if ganador == TresEnRaya.VACIO and not empate:
            lbl = "TURNO:"
            txt_turno = " X " if turno == TresEnRaya.FICHA_X else " O "
            color_t   = NEON_ROSA if turno == TresEnRaya.FICHA_X else NEON_CYAN
            s_lbl = self.fuente_media.render(lbl, True, BLANCO)
            s_val = self.fuente_grande.render(txt_turno, True, color_t)
            pantalla.blit(s_lbl, (ox, oy))
            pantalla.blit(s_val, (ox, oy + 22))
        # estadísticas
        est = self.juego.getEstadisticas()
        oy2 = oy + 80
        pantalla.blit(self.fuente_media.render("ESTADÍSTICAS", True, NEON_AMAR), (ox, oy2))
        oy2 += 24
        items = [
            (f"X gana: {est['victorias_x']}", NEON_ROSA),
            (f"O gana: {est['victorias_o']}", NEON_CYAN),
            (f"Empate: {est['empates']}",     NEON_VERDE),
            (f"Total:  {est['partidas']}",    BLANCO),
        ]
        for txt, col in items:
            pantalla.blit(self.fuente_small.render(txt, True, col), (ox, oy2))
            oy2 += 20
        # tablero actual
        oy2 += 10
        s_tam = self.fuente_small.render(
            f"Tablero: {n}×{n}", True, GRIS_MED)
        pantalla.blit(s_tam, (ox, oy2))
        oy2 += 18 
        # controles
        oy2 += 6
        controles = [
            ("↑↓←→  Mover",  GRIS_MED),
            ("ENTER Jugar",   GRIS_MED),
            ("R     Reiniciar", GRIS_MED),
            ("TAB   3×3 / 4×4", GRIS_MED),
        ]
        for txt, col in controles:
            pantalla.blit(self.fuente_small.render(txt, True, col), (ox, oy2))
            oy2 += 17
 
    def _render_fin(self, pantalla, ganador, empate):
        # panel semi-transparente
        overlay = pygame.Surface((300, 110), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        ox = 20
        oy = self.tablero.y + self.tam_tablero * 3 * self.e + 12
        pantalla.blit(overlay, (ox, oy))
 
        if ganador != TresEnRaya.VACIO:
            nombre  = "X" if ganador == TresEnRaya.FICHA_X else "O"
            color_g = NEON_ROSA if ganador == TresEnRaya.FICHA_X else NEON_CYAN
            s1 = self.fuente_grande.render(f"¡GANÓ  {nombre}!", True, color_g)
            pantalla.blit(s1, (ox + 10, oy + 8))
        else:
            s1 = self.fuente_grande.render("¡EMPATE!", True, NEON_NARAN)
            pantalla.blit(s1, (ox + 10, oy + 8))
 
        s2 = self.fuente_media.render("Presiona R para reiniciar", True, BLANCO)
        pantalla.blit(s2, (ox + 10, oy + 52))
        s3 = self.fuente_small.render("TAB para cambiar tamaño de tablero", True, GRIS_MED)
        pantalla.blit(s3, (ox + 10, oy + 78))

#  GAME LOOP
ANCHO = 500
ALTO  = 450
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Tres en Raya Pro+ ")

clock  = pygame.time.Clock()
escena = EscenaTresEnRaya(tam_tablero=3)
# fondo con degradado simulado
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