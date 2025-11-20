#include <Servo.h>


#define TRIG_PIN 9 
#define ECHO_PIN 8 
const int SERVO_PIN = 10;


const float DISTANCIA_SETPOINT = 15.71;
const int SERVO_NEUTRAL_ANGLE = 65;
const int SERVO_LIMITE_MIN = 25;
const int SERVO_LIMITE_MAX = 140;


float Kp = 4.0;     
float Ki = 0.2;   
float Kd = 450; 

unsigned long tiempo = 0;
unsigned long tiempo_anterior = 0;
unsigned long periodo = 50; 
float error, error_anterior = 0; 
float integral = 0; 
float derivada = 0; 
float salida = 0;

Servo servo;

float DISTANCIA = 0;

float medirDistanciaFiltrada() { 
  const int muestras = 5;
  float suma = 0;
  int validas = 0;

  for (int i = 0; i < muestras; i++) {
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long duracion = pulseIn(ECHO_PIN, HIGH, 20000); 
    float d;

    if (duracion == 0) {
      d = -1;
    } else {
      d = duracion * 0.034 / 2;
    }

    if (d > 0) { 
      suma += d;
      validas++;
    }
    delay(10);
  }

  if (validas == 0) return -1; 
  float promedio = suma / validas;
  return promedio;
}

void setup() {
  Serial.begin(115200);

  servo.attach(SERVO_PIN);
  
  servo.write(90);

  
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  Serial.println("==============================================");
  Serial.println(" SISTEMA DE CONTROL PID - BALANZA Y ESFERA ");
  Serial.println("==============================================");
  Serial.println("Iniciando sistema...");
  Serial.println();
}


float medirDistancia() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);


  long duracion = pulseIn(ECHO_PIN, HIGH, 20000); 

  float DISTANCIA;

  
  if (duracion == 0) {
    DISTANCIA = -1; 
  } else {
    DISTANCIA = duracion * 0.034 / 2; 
  }

  return DISTANCIA; 
}

void loop() {
  tiempo = millis();
  float dt = (tiempo - tiempo_anterior) / 1000.0;
  if (tiempo > tiempo_anterior + periodo) {
    tiempo_anterior = tiempo;

    DISTANCIA = medirDistancia();

    if (DISTANCIA == -1 || DISTANCIA > 30) {
      servo.write(90);
      Serial.println("[INFO] Objeto no detectado o fuera de rango.");
      Serial.println("Servo en posición neutra (90°).");
      Serial.println("----------------------------------------------");
      return;
    }

    if (DISTANCIA > 2 && DISTANCIA < 30) {

      error = DISTANCIA_SETPOINT - DISTANCIA;


      float PID_p = Kp * error;


      float PID_d = Kd * ((error - error_anterior) / dt);


      if (-3 < error && error < 3) {
        integral += Ki * error;
      } else {
        integral = 0;
      }


      salida = PID_p + integral + PID_d;


      salida = map(salida, -150, 150, 0, 150);


      if (salida < 25) salida = 25;
      if (salida > 140) salida = 140;

      float angulo = salida + 30;
      servo.write(angulo);

      Serial.println("----------------------------------------------");
      Serial.print("Tiempo actual: ");
      Serial.print(tiempo / 1000.0, 2);
      Serial.println(" s");

      Serial.print("Distancia medida: ");
      Serial.print(distancia, 2);
      Serial.println(" cm");

      Serial.print("Error actual: ");
      Serial.println(error, 2);

      Serial.print("Componente proporcional (P): ");
      Serial.println(PID_p, 2);

      Serial.print("Componente integral (I): ");
      Serial.println(integral, 2);

      Serial.print("Componente derivativa (D): ");
      Serial.println(PID_d, 2);

      Serial.print("Salida PID total: ");
      Serial.println(salida, 2);

      Serial.print("Ángulo aplicado al servo: ");
      Serial.println(angulo, 2);
      Serial.println("----------------------------------------------");
      
    }

    error_anterior = error;
  }

}
