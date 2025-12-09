import pygame
from collections import deque

from config import *
from simulacion import Balanza, Pelota
# from pid import ControladorPID

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


if __name__ == "__main__":
    main()
