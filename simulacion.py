import pygame
import numpy as np
import random
from config import *

class Sistema:
    def __init__(self):
        self.pos_m = 0.0
        self.vel_m = 0.0
        self.angulo = 0.0
        self.angulo_target = 0.0

    def update(self, dt, control_output):
        MAX_ANG = np.radians(35)
        self.angulo_target = max(min(control_output, MAX_ANG), -MAX_ANG)

        # Simulación servo
        diff = self.angulo_target - self.angulo
        velocidad_servo = 5.0 * dt
        if abs(diff) < velocidad_servo:
            self.angulo = self.angulo_target
        else:
            dist_px = pos_sensor_local - limite_izq
            self.distancia_actual_cm = dist_px / PIXELES_POR_CM

        return self.distancia_actual_cm

    def dibujar(self, superficie, fuente_numeros):
        rad = self.angulo
        cx, cy = self.x, self.y
        w, h = LARGO_VIGA_PX, GROSOR_VIGA

        # Base Estirada
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
