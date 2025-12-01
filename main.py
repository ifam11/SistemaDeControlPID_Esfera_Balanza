import pygame
import math
from config import *
from simulacion import Balanza, Pelota
from pid import ControladorPID   # <<< IMPORTA EL PID

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption(TITULO)
    reloj = pygame.time.Clock()
    
    fuente_medida = pygame.font.SysFont("Arial", 28, bold=True)
    fuente_regla = pygame.font.SysFont("Arial", 10)

    balanza = Balanza(ANCHO // 2, ALTURA_PIVOTE)
    bola = Pelota(ANCHO // 2, 200)

 
    pid = ControladorPID(kp=0.15, ki=0.02, kd=0.18)

    setpoint = 15  

    ejecutando = True
    while ejecutando:
        dt = reloj.get_time() / 1000.0

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

        
        distancia = balanza.leer_sensor(bola)

      
        torque_pid = pid.calcular(setpoint, distancia, dt)

       
        balanza.actualizar_fisica(torque_pid)

       
        pantalla.fill(FONDO)
        pygame.draw.line(pantalla, LINEA_AZUL, (0, ALTURA_PISO), (ANCHO, ALTURA_PISO), 4)
        
        balanza.dibujar(pantalla, fuente_regla)
        bola.dibujar(pantalla)

        texto = fuente_medida.render(f"Distancia: {distancia:.1f} cm", True, NEGRO)
        pantalla.blit(texto, (ANCHO - 300, 50))

        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
