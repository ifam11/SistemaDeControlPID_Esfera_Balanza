import pygame
import math
import time
from pid import ControladorPID 

# Configuración
ANCHO, ALTO = 800, 600
FPS = 60

# Colores
FONDO = (30, 30, 35)
ACERO = (100, 110, 120)
ACERO_OSCURO = (60, 70, 80)
BASE = (50, 50, 50)
NARANJA = (230, 100, 40)
BRILLO = (255, 180, 120)
SENSOR = (200, 50, 50)

# Física
GRAVEDAD = 9.81
LONGITUD_VIGA = 600
GROSOR_VIGA = 14
RADIO_ESFERA = 20
MAX_ANGULO = 0.45 
FACTOR_PESO = 0.003 

# Inicialización
pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Simulación de la balanza con PID")
reloj = pygame.time.Clock()

# PID en ceros para probar solo la física del peso
pid = ControladorPID(kp=0.000, ki=0.000, kd=0.000)

# Variables de estado
bola_pos = 50 
bola_vel = 0
angulo_viga = 0
tiempo_anterior = time.time()
ejecutando = True

def dibujar_rect_rotado(surface, color, cx, cy, w, h, angulo):
    cos_a = math.cos(angulo)
    sin_a = math.sin(angulo)
    hw, hh = w / 2, h / 2
    
    p1 = (cx + (-hw * cos_a - -hh * sin_a), cy + (-hw * sin_a + -hh * cos_a))
    p2 = (cx + (hw * cos_a - -hh * sin_a), cy + (hw * sin_a + -hh * cos_a))
    p3 = (cx + (hw * cos_a - hh * sin_a), cy + (hw * sin_a + hh * cos_a))
    p4 = (cx + (-hw * cos_a - hh * sin_a), cy + (-hw * sin_a + hh * cos_a))

    pygame.draw.polygon(surface, color, [p1, p2, p3, p4])
    pygame.draw.polygon(surface, ACERO_OSCURO, [p1, p2, p3, p4], 2)
    return p1, p2

while ejecutando:
    ahora = time.time()
    dt = ahora - tiempo_anterior
    tiempo_anterior = ahora

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        if evento.type == pygame.MOUSEBUTTONDOWN:
            mouseX, _ = pygame.mouse.get_pos()
            fuerza = -300 if mouseX > ANCHO/2 else 300
            bola_vel += fuerza

    # 1. PID (Fuerza del motor)
    pid_output = pid.calcular(0, bola_pos, dt)

    # 2. Física del Peso (Torque natural)
    # Si la bola está a la derecha (+), inclina la tabla hacia abajo a la derecha (+)
    torque_peso = bola_pos * FACTOR_PESO

    # El ángulo final es la lucha entre el motor (PID) y el peso de la bola
    target_angle = pid_output + torque_peso
    
    # Limitar ángulo
    target_angle = max(-MAX_ANGULO, min(MAX_ANGULO, target_angle))

    # Simulación de inercia de la viga
    diferencia = target_angle - angulo_viga
    angulo_viga += diferencia * 10.0 * dt

    # Física Bola
    # Gravedad alta para sensación de peso
    aceleracion = GRAVEDAD * 200 * math.sin(angulo_viga)
    bola_vel += aceleracion * dt
    bola_pos += bola_vel * dt
    
    bola_vel *= 0.999 # Fricción casi nula

    # Colisiones
    limite_fisico = (LONGITUD_VIGA / 2) - RADIO_ESFERA
    if bola_pos > limite_fisico:
        bola_pos = limite_fisico
        bola_vel *= -0.3
    elif bola_pos < -limite_fisico:
        bola_pos = -limite_fisico
        bola_vel *= -0.3

    # Renderizado
    pantalla.fill(FONDO)
    cx, cy = ANCHO // 2, ALTO // 2 + 50

    pygame.draw.polygon(pantalla, BASE, [(cx, cy), (cx - 50, cy + 100), (cx + 50, cy + 100)])
    extremo_izq, extremo_der = dibujar_rect_rotado(pantalla, ACERO, cx, cy, LONGITUD_VIGA, GROSOR_VIGA, angulo_viga)

    pygame.draw.circle(pantalla, SENSOR, (int(extremo_izq[0]), int(extremo_izq[1])), 6)
    pygame.draw.circle(pantalla, SENSOR, (int(extremo_der[0]), int(extremo_der[1])), 6)

    offset_altura = (GROSOR_VIGA / 2) + RADIO_ESFERA
    bx = cx + bola_pos * math.cos(angulo_viga) + offset_altura * math.sin(angulo_viga)
    by = cy + bola_pos * math.sin(angulo_viga) - offset_altura * math.cos(angulo_viga)

    pygame.draw.circle(pantalla, NARANJA, (int(bx), int(by)), RADIO_ESFERA)
    pygame.draw.circle(pantalla, (50, 20, 0), (int(bx), int(by)), RADIO_ESFERA, 1)
    pygame.draw.circle(pantalla, BRILLO, (int(bx - 5), int(by - 5)), 6)

    pygame.display.flip()
    reloj.tick(FPS)

pygame.quit()