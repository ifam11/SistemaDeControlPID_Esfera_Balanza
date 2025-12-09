import pygame
from collections import deque

from config import *
from pid import PID
from simulacion import Sistema, dibujar_todo_realista

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Simulación PID Realista - V6 Final")
    reloj = pygame.time.Clock()

    sys = Sistema()
    pid = PID(KP, KI, KD, SETPOINT_CM)

    hist_pos = deque(maxlen=ANCHO // 2)
    hist_set = deque(maxlen=ANCHO // 2)
    hist_ang = deque(maxlen=ANCHO // 2)

    arrastrando = False

    while True:
        dt = reloj.tick(FPS) / 1000.0
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if my < SUELO_Y:
                    arrastrando = True
                    sys.vel_m = 0
            elif event.type == pygame.MOUSEBUTTONUP:
                arrastrando = False
                pid.reset()

        medicion_cm = sys.leer_sensor_cm()

        if arrastrando:
            dx_px = mx - CX
            pos_m_mouse = dx_px / ESCALA

            limite = (L_RIEL_M / 2.0) - (RADIO_BOLA_PX / ESCALA)
            sys.pos_m = max(min(pos_m_mouse, limite), -limite)
            sys.vel_m = 0
            sys.update(dt, 0.0)
        else:
            output = pid.calcular(medicion_cm, dt)
            sys.update(dt, -output)

        hist_pos.append(medicion_cm)
        hist_set.append(SETPOINT_CM)
        hist_ang.append(sys.angulo)

        dibujar_todo_realista(pantalla, sys, hist_pos, hist_set, hist_ang, arrastrando)

        font_big = pygame.font.SysFont("Arial", 24, bold=True)
        if arrastrando:
            txt = font_big.render("MODO MANUAL - SOLTAR PARA ACTIVAR PID", True, (255, 255, 0))
        else:
            txt = font_big.render("CONTROL PID ACTIVO", True, (200, 200, 200))

        pantalla.blit(txt, (CX - txt.get_width() // 2, 30))
        pygame.display.flip()

if __name__ == "__main__":
    main()
