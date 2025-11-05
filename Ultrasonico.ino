#include <Servo.h>


#define TRIG_PIN 9 //Pin del US
#define ECHO_PIN 8 //Pin del US
#define SERVO_PIN 10 //Pin del Servo


float setpoint = 15.0; // distancia objetivo (cm)
float distancia = 0;
float error, error_anterior = 0;
float integral = 0;
float derivada = 0;
float salida = 0;

float Kp = 4.0;   // Proporcional
float Ki = 0.5;   // Integral
float Kd = 2.0;   // Derivativo

Servo servo;

void setup() {
  Serial.begin(9600);
  servo.attach(SERVO_PIN);
  servo.write(90); // posición neutra
  
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  Serial.println("Sistema PID Balanza y Bola Iniciado");
}

// Función para medir distancia
float medirDistancia() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  long duracion = pulseIn(ECHO_PIN, HIGH, 20000); // límite de 20 ms
  float distancia = duracion * 0.034 / 2;
  return distancia;
}

void loop() {
  distancia = medirDistancia();
  
  if (distancia > 2 && distancia < 30) { // rango válido del sensor
    // Cálculo del error
    error = setpoint - distancia;
    integral += error;
    derivada = error - error_anterior;

    // Cálculo PID
    salida = Kp * error + Ki * integral + Kd * derivada;

    // Convertir la salida PID en ángulo del servo
    float angulo = 90 + salida;
    angulo = constrain(angulo, 60, 120); // límites de inclinación
    
    servo.write(angulo);

    // Monitoreo Serial
    Serial.print("Distancia: ");
    Serial.print(distancia);
    Serial.print(" cm | Error: ");
    Serial.print(error);
    Serial.print(" | Salida PID: ");
    Serial.print(salida);
    Serial.print(" | Angulo Servo: ");
    Serial.println(angulo);

    error_anterior = error;
  }
  
  delay(50);
}
