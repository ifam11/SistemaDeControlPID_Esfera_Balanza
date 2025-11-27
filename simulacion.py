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
pygame.font.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Simulación de la balanza con PID")
reloj = pygame.time.Clock()

# PID con valores para probar
controlador = ControladorPID(
    kp=0.11,
    ki=0.0015,
    kd=0.0035,
    output_limits=(-0.5, 0.5),    # límite de la salida del PID (representa parte del ángulo objetivo)
    integral_limit=0.5,          # anti-windup: límite absoluto de la integral
    deriv_filter_alpha=0.7       # filtrado exponencial para la derivada (0..1)
)
# Variables de estado
bola_pos = 50 
bola_vel = 0
angulo_viga = 0
tiempo_anterior = time.time()
ejecutando = True

punto_referencia = 0.0      # setpoint en mismas unidades que pos_bola
pausado = False
mostrar_info = True
registrar = False           # control de logging a CSV
tiempo_inicio = time.time()
fuente = pygame.font.SysFont("consolas", 16)

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
            if evento.button == 1:
                fuerza = -300 if mouseX > ANCHO/2 else 300
                bola_vel += fuerza
            elif evento.button == 3:
                    # convertir coordenada de píxeles a unidades de pos_bola
                    rel_x = mouseX - (ANCHO // 2)
                    escala = (LONGITUD_VIGA / 2) / (ANCHO / 2)
                    punto_referencia = max(- (LONGITUD_VIGA / 2 - RADIO_ESFERA),
                                        min((LONGITUD_VIGA / 2 - RADIO_ESFERA), rel_x * escala))
      
        # ---------------------------
        # Manejo de teclado: pausa, reset, mostrar info, tuning en tiempo real, logging
        # ---------------------------
        # ### MODIFICACIÓN:
        # - Teclas Q/A: incrementar/disminuir kp
        # - Teclas W/S: incrementar/disminuir ki
        # - Teclas E/D: incrementar/disminuir kd
        # - R: reset del PID (limpia integral y errores previos)
        # - SPACE: pausa
        # - I: mostrar/ocultar info
        # - L: activar/desactivar logging a CSV
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                pausado = not pausado
            elif evento.key == pygame.K_r:
                controlador.reset()
            elif evento.key == pygame.K_i:
                mostrar_info = not mostrar_info
            elif evento.key == pygame.K_q:
                controlador.kp += 0.0005
            elif evento.key == pygame.K_a:
                controlador.kp = max(0.0, controlador.kp - 0.0005)
            elif evento.key == pygame.K_w:
                controlador.ki += 0.0001
            elif evento.key == pygame.K_s:
                controlador.ki = max(0.0, controlador.ki - 0.0001)
            elif evento.key == pygame.K_e:
                controlador.kd += 0.0002
            elif evento.key == pygame.K_d:
                controlador.kd = max(0.0, controlador.kd - 0.0002)
            elif evento.key == pygame.K_l:
                registrar = not registrar
                if registrar:
                    # Crear/reescribir archivo CSV de registro
                    with open("registro_simulacion.csv", "w") as f:
                        f.write("t,bola_pos,punto_referencia,angulo_viga,kp,ki,kd\n")

    if pausado:
        # Mantener renderizado pero no actualizar estados físicos
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

        # Mostrar información si está activada
        if mostrar_info:
            error = punto_referencia - bola_pos
            lineas = [
                f"KP: {controlador.kp:.6f}  KI: {controlador.ki:.6f}  KD: {controlador.kd:.6f}",
                f"Pos bola: {bola_pos:.2f}  Referencia: {punto_referencia:.2f}  Error: {error:.2f}",
                f"Angulo viga: {angulo_viga:.4f}",
                f"Pausa: {'ON' if pausado else 'OFF'}  Logging: {'ON' if registrar else 'OFF'}",
                "Teclas: Q/A kp, W/S ki, E/D kd, R reset, SPACE pausa, I info, L log, R-click setpoint"
            ]
            for i, txt in enumerate(lineas):
                surf = fuente.render(txt, True, (220, 220, 220))
                pantalla.blit(surf, (10, 10 + i * 18))

        pygame.display.flip()
        reloj.tick(FPS)
        continue 
    # 1. PID (Fuerza del motor)
    salida_pid = controlador.calcular(punto_referencia, bola_pos, dt)

    # 2. Física del Peso (Torque natural)
    # Si la bola está a la derecha (+), inclina la tabla hacia abajo a la derecha (+)
    torque_peso = bola_pos * FACTOR_PESO

    # El ángulo final es la lucha entre el motor (PID) y el peso de la bola
    angulo_objetivo = salida_pid + torque_peso
    angulo_objetivo = max(-MAX_ANGULO, min(MAX_ANGULO, angulo_objetivo))
    

    # Simulación de inercia de la viga
    diferencia = angulo_objetivo  - angulo_viga
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

    if registrar:
        t = time.time() - tiempo_inicio
        with open("registro_simulacion.csv", "a") as f:
            f.write(f"{t:.4f},{bola_pos:.4f},{punto_referencia:.4f},{angulo_viga:.6f},{controlador.kp:.6f},{controlador.ki:.6f},{controlador.kd:.6f}\n")

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

    if mostrar_info:
        error = punto_referencia - bola_pos
        lineas = [
            f"KP: {controlador.kp:.6f}  KI: {controlador.ki:.6f}  KD: {controlador.kd:.6f}",
            f"Pos bola: {bola_pos:.2f}  Referencia: {punto_referencia:.2f}  Error: {error:.2f}",
            f"Angulo viga: {angulo_viga:.4f}  PID_out: {salida_pid:.4f}",
            f"Pausa: {'ON' if pausado else 'OFF'}  Logging: {'ON' if registrar else 'OFF'}",
            "Teclas: Q/A kp, W/S ki, E/D kd, R reset, SPACE pausa, I info, L log, R-click setpoint"
        ]
        for i, txt in enumerate(lineas):
            surf = fuente.render(txt, True, (220, 220, 220))
            pantalla.blit(surf, (10, 10 + i * 18))


    pygame.display.flip()
    reloj.tick(FPS)

pygame.quit()