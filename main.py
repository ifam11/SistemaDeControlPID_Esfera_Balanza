import pygame
import math
from config import *
from simulacion import Balanza, Pelota
from pid import ControladorPID

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption(TITULO)
    reloj = pygame.time.Clock()
    
    fuente_medida = pygame.font.SysFont("Arial", 28, bold=True)
    fuente_regla = pygame.font.SysFont("Arial", 10)

    balanza = Balanza(ANCHO // 2, ALTURA_PIVOTE)
    bola = Pelota(ANCHO // 2, 200)

    
    pid = ControladorPID(kp=0.015, ki=0.0004, kd=0.008)

   
    angulo = 0.0
    vel_angular = 0.0

    inercia = 0.35
    friccion = 0.15

    ejecutando = True
    while ejecutando:
        dt = reloj.tick(FPS) / 1000.0

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if math.hypot(mx - bola.x, my - bola.y) < RADIO_BOLA_PX * 2:
                    bola.agarrada = True
            
            if evento.type == pygame.MOUSEBUTTONUP:
                bola.agarrada = False

      
        bola.actualizar(balanza)

        
        distancia = bola.x - balanza.x    

        
        setpoint = 0

      
        torque_pid = pid.calcular(setpoint, distancia, dt)

      
        torque_pid = max(min(torque_pid, 6.0), -6.0)

       
        torque_total = torque_pid - friccion * vel_angular
        aceleracion = torque_total / inercia

        vel_angular += aceleracion * dt
        angulo += vel_angular * dt

        
        angulo = max(min(angulo, 0.8), -0.8)

        balanza.angulo = angulo

        
        pantalla.fill(FONDO)
        pygame.draw.line(pantalla, LINEA_AZUL, (0, ALTURA_PISO), (ANCHO, ALTURA_PISO), 4)

        balanza.dibujar(pantalla, fuente_regla)
        bola.dibujar(pantalla)

        texto = fuente_medida.render(f"Error: {distancia:.1f} px", True, NEGRO)
        pantalla.blit(texto, (ANCHO - 300, 50))

        texto2 = fuente_medida.render(f"Ángulo: {angulo:.2f} rad", True, NEGRO)
        pantalla.blit(texto2, (ANCHO - 300, 90))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
