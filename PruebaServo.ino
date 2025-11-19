#include <Servo.h>

const int SERVO_PIN = 10;
const int ANGULO_MINIMO_PRUEBA = 0;
const int ANGULO_MAXIMO_PRUEBA = 180;

Servo miServo;

void setup() {
  Serial.begin(9600);
  miServo.attach(SERVO_PIN);
  
  Serial.println("Herramienta de Prueba de Servomotor");
  Serial.println("Envia un angulo para mover el servo.");
  
  delay(1000);
  
  miServo.write(15);
  Serial.println("Servo iniciado en 15 grados.");
}

void loop() {
  controlManual();
}

void controlManual() {
  if (Serial.available() > 0) {
    int anguloDeseado = Serial.parseInt();
    
    if (anguloDeseado > 0 || Serial.peek() == '0') {
      Serial.print("Moviendo a: ");
      Serial.print(anguloDeseado);
      Serial.println(" grados.");
      
      miServo.write(anguloDeseado);
    }
    
    while (Serial.available() > 0) {
      Serial.read();
    }
  }
}

// GRADO MAXIMO 140 
// GRADO MINIMO 25
// CENTRO 80