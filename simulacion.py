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
            self.angulo += velocidad_servo * np.sign(diff)

        # Física
        accel = (5.0 / 7.0) * GRAVEDAD * np.sin(self.angulo)
        self.vel_m += accel * dt
        self.vel_m *= 0.995
        self.pos_m += self.vel_m * dt

        # Topes físicos
        limite_m = (L_RIEL_M / 2.0) - (RADIO_BOLA_PX / ESCALA)
        if self.pos_m > limite_m:
            self.pos_m, self.vel_m = limite_m, 0
        elif self.pos_m < -limite_m:
            self.pos_m, self.vel_m = -limite_m, 0

    def leer_sensor_cm(self):
        lectura = 15.0 - (self.pos_m * 100.0)
        return lectura + random.gauss(0, 0.05)

# ---------- DIBUJO ----------

def dibujar_gradiente_riel(surf, p1, p2, ancho):
    vec = np.array(p2) - np.array(p1)
    longitud = np.linalg.norm(vec)
    angulo = np.arctan2(vec[1], vec[0])

    surf_riel = pygame.Surface((int(longitud), ancho), pygame.SRCALPHA)

    pygame.draw.rect(surf_riel, ALUMINIO_OSCURO, (0, 0, longitud, ancho))
    pygame.draw.rect(surf_riel, ALUMINIO_CLARO, (0, 2, longitud, ancho - 4))
    pygame.draw.rect(surf_riel, (255, 255, 255), (0, 5, longitud, 4))

    surf_rot = pygame.transform.rotate(surf_riel, -np.degrees(angulo))
    rect = surf_rot.get_rect(center=((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2))
    surf.blit(surf_rot, rect)


def dibujar_base_madera(surf):
    pygame.draw.rect(surf, MESA_TOP, (0, SUELO_Y, ANCHO, ALTO - SUELO_Y))

    base_rect = pygame.Rect(CX - 150, SUELO_Y, 300, 30)
    pygame.draw.rect(surf, MADERA_CLARO, base_rect)
    pygame.draw.rect(surf, MADERA_OSCURO, base_rect, 3)

    for i in range(CX - 140, CX + 150, 20):
        pygame.draw.line(surf, MADERA_OSCURO, (i, SUELO_Y), (i + 10, SUELO_Y + 30), 1)

    box_x, box_y = CX + 180, SUELO_Y - 50
    pygame.draw.rect(surf, (10, 10, 10), (box_x, box_y, 140, 60), border_radius=5)
    pygame.draw.rect(surf, (0, 30, 0), (box_x + 10, box_y + 10, 120, 40))
    pygame.draw.rect(surf, LCD_FONDO, (box_x + 10, box_y + 10, 120, 40), 2)

    return box_x, box_y


def dibujar_sensor_sharp(surf, end_x, end_y, angulo):
    cos_a, sin_a = np.cos(angulo), np.sin(angulo)

    offset_h = ANCHO_RIEL / 2 + 20
    sx = end_x + offset_h * sin_a
    sy = end_y - offset_h * cos_a

    img_sensor = pygame.Surface((40, 20), pygame.SRCALPHA)
    pygame.draw.rect(img_sensor, (20, 20, 20), (5, 5, 30, 10))
    pygame.draw.circle(img_sensor, (40, 0, 0), (12, 10), 4)
    pygame.draw.circle(img_sensor, (40, 0, 0), (28, 10), 4)

    img_rot = pygame.transform.rotate(img_sensor, -np.degrees(angulo))
    rect = img_rot.get_rect(center=(sx, sy))
    surf.blit(img_rot, rect)

    base_x = end_x + (ANCHO_RIEL / 2) * sin_a
    base_y = end_y - (ANCHO_RIEL / 2) * cos_a
    pygame.draw.line(surf, AZUL_SERVO, (base_x, base_y), (sx, sy), 4)

    end_ray_x = sx - 600 * cos_a
    end_ray_y = sy - 600 * sin_a
    pygame.draw.line(surf, (255, 0, 0, 20), (sx, sy), (end_ray_x, end_ray_y), 1)


def dibujar_osciloscopio(surf, hist_p, hist_s, hist_a):
    rect = pygame.Rect(50, SUELO_Y + 30, ANCHO - 100, ALTO - SUELO_Y - 50)
    pygame.draw.rect(surf, (10, 15, 20), rect)
    pygame.draw.rect(surf, (50, 60, 70), rect, 2)

    mid_y = rect.centery
    pygame.draw.line(surf, (0, 100, 0), (rect.left, mid_y), (rect.right, mid_y), 1)

    if len(hist_p) > 2:
        pts_pos, pts_set, pts_srv = [], [], []
        scale_y = 8

        for i in range(len(hist_p)):
            x = rect.right - (len(hist_p) - i) * 2
            if x < rect.left:
                continue

            err_pos = (hist_p[i] - 15.0)
            err_set = (hist_s[i] - 15.0)

            pts_pos.append((x, mid_y - err_pos * scale_y))
            pts_set.append((x, mid_y - err_set * scale_y))
            pts_srv.append((x, mid_y - np.degrees(hist_a[i]) * 1.5))

        pygame.draw.lines(surf, ROJO_BOLA, False, pts_pos, 2)
        pygame.draw.lines(surf, (0, 255, 0), False, pts_set, 1)
        pygame.draw.lines(surf, AZUL_SERVO, False, pts_srv, 1)


def dibujar_todo_realista(surf, sys, hist_p, hist_s, hist_a, arrastrando):
    surf.fill(FONDO_LAB)

    theta = sys.angulo
    cos_t, sin_t = np.cos(theta), np.sin(theta)

    box_x, box_y = dibujar_base_madera(surf)

    # Pivote
    p1 = (CX - 30, SUELO_Y)
    p2 = (CX + 30, SUELO_Y)
    p3 = (CX, CY)
    pygame.draw.polygon(surf, AZUL_OSCURO, [p1, p2, p3])
    pygame.draw.line(surf, AZUL_SERVO, p1, p3, 2)
    pygame.draw.line(surf, AZUL_SERVO, p2, p3, 2)

    servo_x = CX - L_RIEL_PX/2 + 40
    servo_y = SUELO_Y - 45

    pygame.draw.rect(surf, (20, 20, 25), (servo_x-15, servo_y-15, 30, 30)) 
    pygame.draw.circle(surf, AZUL_SERVO, (servo_x, servo_y), 18) # Rueda
    
    # Brazo del servo
    wheel_ang = -theta * 4 + np.pi/2
    wx = servo_x + 18 * np.cos(wheel_ang)
    wy = servo_y + 18 * np.sin(wheel_ang)
    pygame.draw.line(surf, (255, 255, 255), (servo_x, servo_y), (wx, wy), 3)
    
    # Varilla de conexión
    conn_x = CX - (L_RIEL_PX/2 - 40) * cos_t + (ANCHO_RIEL/2 + 5)*sin_t
    conn_y = CY - (L_RIEL_PX/2 - 40) * sin_t - (ANCHO_RIEL/2 + 5)*cos_t
    pygame.draw.line(surf, (200, 200, 200), (wx, wy), (conn_x, conn_y), 3)

    # Riel
    x1 = CX - (L_RIEL_PX / 2) * cos_t
    y1 = CY - (L_RIEL_PX / 2) * sin_t
    x2 = CX + (L_RIEL_PX / 2) * cos_t
    y2 = CY + (L_RIEL_PX / 2) * sin_t

    pygame.draw.line(surf, (0, 0, 0), (x1, SUELO_Y), (x2, SUELO_Y), ANCHO_RIEL)
    dibujar_gradiente_riel(surf, (x1, y1), (x2, y2), ANCHO_RIEL)

    dibujar_sensor_sharp(surf, x2, y2, theta)

    # Bola
    dist_px = sys.pos_m * ESCALA
    offset_v = RADIO_BOLA_PX + (ANCHO_RIEL / 2)

    bx = CX + dist_px * cos_t + offset_v * sin_t
    by = CY + dist_px * sin_t - offset_v * cos_t

    color = ROJO_BOLA if not arrastrando else (255, 255, 100)
    pygame.draw.circle(surf, color, (int(bx), int(by)), RADIO_BOLA_PX)

    # LCD
    font_lcd = pygame.font.SysFont("Consolas", 20, bold=True)
    lectura = sys.leer_sensor_cm()
    txt_lcd = font_lcd.render(f"{lectura:.1f} cm", True, LCD_TEXTO)
    surf.blit(txt_lcd, (box_x + 20, box_y + 18))

    # Gráfica
    dibujar_osciloscopio(surf, hist_p, hist_s, hist_a)
