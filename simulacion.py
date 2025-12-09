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
        # Péndulo simple
        torque_gravedad = -0.08 * math.sin(self.angulo)
        
        accel = (torque_bola + torque_gravedad) * 0.1
        self.vel_angular += accel
        self.vel_angular *= 0.96
        self.angulo += self.vel_angular
        
        if self.angulo > 0.5: self.angulo = 0.5; self.vel_angular *= -0.2
        if self.angulo < -0.5: self.angulo = -0.5; self.vel_angular *= -0.2

    def leer_sensor(self, bola):
        # 1. Geometría
        mitad_ancho = LARGO_VIGA_PX / 2
        pos_sensor_local = mitad_ancho - GROSOR_TOPE
        
        # 2. Posición local bola
        dx = bola.x - self.x
        dy = bola.y - self.y
        cos_inv = math.cos(-self.angulo)
        sin_inv = math.sin(-self.angulo)
        local_x = dx * cos_inv - dy * sin_inv
        local_y = dx * sin_inv + dy * cos_inv

        # 3. ¿El sensor ve la bola? (CORRECCIÓN DE ALTURA)
        limite_izq = -mitad_ancho + GROSOR_TOPE
        limite_der = mitad_ancho - GROSOR_TOPE
        
        # Calculamos dónde está la bola cuando rueda sobre la viga
        # Altura superficie = -GROSOR_VIGA/2 (-12.5 px)
        # Centro bola = Altura superficie - RADIO_BOLA_PX (-30 px) -> Total: -42.5 px
        altura_reposo = - (GROSOR_VIGA / 2) - RADIO_BOLA_PX 
        
        # Definimos el "Haz del Láser":
        # Si la bola sube un poco (rebote) el sensor aún la ve.
        # Pero si sube más de 1.5 radios (aprox 45px hacia arriba), el láser pasa por debajo.
        # Rango válido: Desde un poco abajo de la superficie (por error gráfico) hasta 1.5 radios arriba.
        limite_altura_superior = altura_reposo - (RADIO_BOLA_PX * 1.5) # Si sube más que esto, no se ve
        
        # Condición estricta:
        # 1. Estar horizontalmente entre los topes
        # 2. Estar verticalmente tocando o casi tocando la viga
        en_rango = (limite_izq < local_x < limite_der) and (limite_altura_superior < local_y < 10)

        if en_rango:
            # El sensor ve la bola
            dist_px = pos_sensor_local - local_x - RADIO_BOLA_PX
            self.distancia_actual_cm = dist_px / PIXELES_POR_CM
            if self.distancia_actual_cm < 0: self.distancia_actual_cm = 0
        else:
            # El sensor NO ve la bola (está volando muy alto o fuera de límites)
            # Mide hasta el tope izquierdo (Fondo de escala)
            dist_px = pos_sensor_local - limite_izq
            self.distancia_actual_cm = dist_px / PIXELES_POR_CM

        return self.distancia_actual_cm

    def dibujar(self, superficie, fuente_numeros):
        rad = self.angulo
        cx, cy = self.x, self.y
        w, h = LARGO_VIGA_PX, GROSOR_VIGA

        # Base
        pygame.draw.polygon(superficie, BASE_OSCURA, [(cx, cy), (cx-40, ALTURA_PISO), (cx+40, ALTURA_PISO)])
        pygame.draw.circle(superficie, (150,150,150), (cx, cy), 8)

        # Viga
        p1 = rotar(cx - w/2, cy - h/2, cx, cy, rad)
        p2 = rotar(cx + w/2, cy - h/2, cx, cy, rad)
        p3 = rotar(cx + w/2, cy + h/2, cx, cy, rad)
        p4 = rotar(cx - w/2, cy + h/2, cx, cy, rad)
        pygame.draw.polygon(superficie, MADERA_CLARA, [p1, p2, p3, p4])
        pygame.draw.polygon(superficie, MADERA_OSCURA, [p1, p2, p3, p4], 2)

        # Topes
        alto_tope = 30
        t1 = rotar(cx - w/2, cy - h/2 - alto_tope, cx, cy, rad)
        t2 = rotar(cx - w/2 + GROSOR_TOPE, cy - h/2 - alto_tope, cx, cy, rad)
        t3 = rotar(cx - w/2 + GROSOR_TOPE, cy - h/2, cx, cy, rad)
        pygame.draw.polygon(superficie, MADERA_OSCURA, [t1, t2, t3, p1]) 

        s1 = rotar(cx + w/2 - GROSOR_TOPE, cy - h/2 - alto_tope, cx, cy, rad)
        s2 = rotar(cx + w/2, cy - h/2 - alto_tope, cx, cy, rad)
        s4 = rotar(cx + w/2 - GROSOR_TOPE, cy - h/2, cx, cy, rad)
        pygame.draw.polygon(superficie, ROJO_SENSOR, [s1, s2, p2, s4])

        # Regla
        for cm in range(0, LARGO_VIGA_CM + 1):
            x_local = (cm - 15) * PIXELES_POR_CM
            if x_local < -w/2 + GROSOR_TOPE or x_local > w/2 - GROSOR_TOPE: continue
            largo = 15 if cm % 5 == 0 else 8
            m_top = rotar(cx + x_local, cy - h/2, cx, cy, rad)
            m_bot = rotar(cx + x_local, cy - h/2 + largo, cx, cy, rad)
            pygame.draw.line(superficie, TEXTO_REGLA, m_top, m_bot, 1)
            if cm % 5 == 0:
                pos = rotar(cx + x_local, cy + 5, cx, cy, rad)
                txt = fuente_numeros.render(str(cm), True, TEXTO_REGLA)
                rect = txt.get_rect(center=(int(pos[0]), int(pos[1])))
                superficie.blit(txt, rect)

        # Láser
        inicio_laser = rotar(cx + w/2 - GROSOR_TOPE, cy - h/2 - RADIO_BOLA_PX/2, cx, cy, rad)
        largo_laser_px = self.distancia_actual_cm * PIXELES_POR_CM
        fin_laser_x = inicio_laser[0] - math.cos(rad) * largo_laser_px
        fin_laser_y = inicio_laser[1] - math.sin(rad) * largo_laser_px
        pygame.draw.line(superficie, LASER, inicio_laser, (fin_laser_x, fin_laser_y), 2)