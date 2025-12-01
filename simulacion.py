import pygame
import math
from config import *

def rotar(x, y, cx, cy, angulo):
    cos_a = math.cos(angulo)
    sin_a = math.sin(angulo)
    dx = x - cx
    dy = y - cy
    return cx + (dx * cos_a - dy * sin_a), cy + (dx * sin_a + dy * cos_a)


class Balanza:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.angulo = 0.0
        self.vel_angular = 0.0
        self.distancia_actual_cm = 0.0

    def actualizar_fisica(self, torque_bola):
        torque_gravedad = -0.08 * math.sin(self.angulo)

        accel = (torque_bola + torque_gravedad) * 0.2
        self.vel_angular += accel
        self.vel_angular *= 0.90
        self.angulo += self.vel_angular

        if self.angulo > 0.5:
            self.angulo = 0.5
            self.vel_angular *= -0.25

        if self.angulo < -0.5:
            self.angulo = -0.5
            self.vel_angular *= -0.25


    def leer_sensor(self, bola):
        mitad_ancho = LARGO_VIGA_PX / 2
        pos_sensor_local = mitad_ancho - GROSOR_TOPE

        dx = bola.x - self.x
        dy = bola.y - self.y

        cos_inv = math.cos(-self.angulo)
        sin_inv = math.sin(-self.angulo)

        local_x = dx * cos_inv - dy * sin_inv
        local_y = dx * sin_inv + dy * cos_inv

        limite_izq = -mitad_ancho + GROSOR_TOPE
        limite_der = mitad_ancho - GROSOR_TOPE

        altura_reposo = - (GROSOR_VIGA / 2) - RADIO_BOLA_PX
        limite_altura_superior = altura_reposo - (RADIO_BOLA_PX * 1.5)

        en_rango = (limite_izq < local_x < limite_der) and (limite_altura_superior < local_y < 10)

        if en_rango:
            dist_px = pos_sensor_local - local_x - RADIO_BOLA_PX
            self.distancia_actual_cm = max(dist_px / PIXELES_POR_CM, 0)
        else:
            dist_px = pos_sensor_local - limite_izq
            self.distancia_actual_cm = dist_px / PIXELES_POR_CM

        return self.distancia_actual_cm


    def dibujar(self, superficie, fuente_numeros):
        rad = self.angulo
        cx, cy = self.x, self.y
        w, h = LARGO_VIGA_PX, GROSOR_VIGA

        pygame.draw.polygon(superficie, BASE_OSCURA, [(cx, cy), (cx-40, ALTURA_PISO), (cx+40, ALTURA_PISO)])
        pygame.draw.circle(superficie, (150,150,150), (cx, cy), 8)

        p1 = rotar(cx - w/2, cy - h/2, cx, cy, rad)
        p2 = rotar(cx + w/2, cy - h/2, cx, cy, rad)
        p3 = rotar(cx + w/2, cy + h/2, cx, cy, rad)
        p4 = rotar(cx - w/2, cy + h/2, cx, cy, rad)

        pygame.draw.polygon(superficie, MADERA_CLARA, [p1, p2, p3, p4])
        pygame.draw.polygon(superficie, MADERA_OSCURA, [p1, p2, p3, p4], 2)

        alto_tope = 30

        t1 = rotar(cx - w/2, cy - h/2 - alto_tope, cx, cy, rad)
        t2 = rotar(cx - w/2 + GROSOR_TOPE, cy - h/2 - alto_tope, cx, cy, rad)
        t3 = rotar(cx - w/2 + GROSOR_TOPE, cy - h/2, cx, cy, rad)

        pygame.draw.polygon(superficie, MADERA_OSCURA, [t1, t2, t3, p1])

        s1 = rotar(cx + w/2 - GROSOR_TOPE, cy - h/2 - alto_tope, cx, cy, rad)
        s2 = rotar(cx + w/2, cy - h/2 - alto_tope, cx, cy, rad)
        s4 = rotar(cx + w/2 - GROSOR_TOPE, cy - h/2, cx, cy, rad)

        pygame.draw.polygon(superficie, ROJO_SENSOR, [s1, s2, p2, s4])

        for cm in range(0, LARGO_VIGA_CM + 1):
            x_local = (cm - 15) * PIXELES_POR_CM

            if x_local < -w/2 + GROSOR_TOPE or x_local > w/2 - GROSOR_TOPE:
                continue

            largo = 15 if cm % 5 == 0 else 8

            m_top = rotar(cx + x_local, cy - h/2, cx, cy, rad)
            m_bot = rotar(cx + x_local, cy - h/2 + largo, cx, cy, rad)

            pygame.draw.line(superficie, TEXTO_REGLA, m_top, m_bot, 1)

            if cm % 5 == 0:
                pos = rotar(cx + x_local, cy + 5, cx, cy, rad)
                txt = fuente_numeros.render(str(cm), True, TEXTO_REGLA)
                rect = txt.get_rect(center=(int(pos[0]), int(pos[1])))
                superficie.blit(txt, rect)

        inicio_laser = rotar(cx + w/2 - GROSOR_TOPE, cy - h/2 - RADIO_BOLA_PX/2, cx, cy, rad)
        largo_laser_px = self.distancia_actual_cm * PIXELES_POR_CM

        fin_laser_x = inicio_laser[0] - math.cos(rad) * largo_laser_px
        fin_laser_y = inicio_laser[1] - math.sin(rad) * largo_laser_px

        pygame.draw.line(superficie, LASER, inicio_laser, (fin_laser_x, fin_laser_y), 2)


class Pelota:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx, self.vy = 0, 0
        self.agarrada = False

    def actualizar(self, balanza):

        if self.agarrada:
            mx, my = pygame.mouse.get_pos()
            self.x, self.y = mx, my
            self.vx, self.vy = 0, 0
            return

        self.vy += GRAVEDAD
        self.x += self.vx
        self.y += self.vy

        if self.x < RADIO_BOLA_PX:
            self.x = RADIO_BOLA_PX
            self.vx *= -REBOTE_PAREDES

        if self.x > ANCHO - RADIO_BOLA_PX:
            self.x = ANCHO - RADIO_BOLA_PX
            self.vx *= -REBOTE_PAREDES

        if self.y < RADIO_BOLA_PX:
            self.y = RADIO_BOLA_PX
            self.vy *= -REBOTE_PAREDES

        if self.y > ALTURA_PISO - RADIO_BOLA_PX:
            self.y = ALTURA_PISO - RADIO_BOLA_PX
            self.vy *= -REBOTE_SUELO
            self.vx *= 0.9

        self._resolver_colision_viga(balanza)

    def _resolver_colision_viga(self, balanza):
        dx = self.x - balanza.x
        dy = self.y - balanza.y

        cos_inv = math.cos(-balanza.angulo)
        sin_inv = math.sin(-balanza.angulo)

        local_x = dx * cos_inv - dy * sin_inv
        local_y = dx * sin_inv + dy * cos_inv

        mitad_w = LARGO_VIGA_PX / 2
        mitad_h = GROSOR_VIGA / 2

        limite_izq = -mitad_w + GROSOR_TOPE + RADIO_BOLA_PX
        limite_der = mitad_w - GROSOR_TOPE - RADIO_BOLA_PX

        if local_x < limite_izq:
            local_x = limite_izq
        if local_x > limite_der:
            local_x = limite_der

        local_y = -mitad_h - RADIO_BOLA_PX

        self.x = balanza.x + (local_x * math.cos(balanza.angulo) - local_y * math.sin(balanza.angulo))
        self.y = balanza.y + (local_x * math.sin(balanza.angulo) + local_y * math.cos(balanza.angulo))

    def dibujar(self, superficie):
        pygame.draw.circle(superficie, NEGRO, (int(self.x), int(self.y)), RADIO_BOLA_PX)
        pygame.draw.circle(superficie, (80, 80, 80), (int(self.x - 5), int(self.y - 5)), 5)
