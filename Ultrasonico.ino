#include <Servo.h>


#define TRIG_PIN 9 
#define ECHO_PIN 8 



float setpoint = 15.0; 

float distancia = 0;
float error, error_anterior = 0;
float integral = 0;
float derivada = 0;
float salida = 0;


float Kp = 8;     
float Ki = 0.2;   
float Kd = 3100; 

unsigned long tiempo = 0;
unsigned long tiempo_anterior = 0;
unsigned long periodo = 50; 

Servo servo;

void setup() {
  Serial.begin(9600);

  servo.attach(10);
  
  servo.write(90);

  
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  Serial.println("Sistema PID Balanza y Bola Iniciado");
}


float medirDistancia() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);


  long duracion = pulseIn(ECHO_PIN, HIGH, 20000); 

  float distancia;

  
  if (duracion == 0) {
    distancia = -1; 
  } else {
    distancia = duracion * 0.034 / 2; 
  }

  return distancia; 
}

void loop() {
  tiempo = millis();
  if (tiempo > tiempo_anterior + periodo) {
    tiempo_anterior = tiempo;

    distancia = medirDistancia();

    if (distancia == -1 || distancia > 30) {
      servo.write(90);
      Serial.println("Objeto no detectado o fuera de rango. Por lo tanto posición del Servo en neutro (90°).");
      return;
    }

    if (distancia > 2 && distancia < 30) {

      error = setpoint - distancia;


      float PID_p = Kp * error;


      float PID_d = Kd * ((error - error_anterior) / periodo);


      if (-3 < error && error < 3) {
        integral += Ki * error;
      } else {
        integral = 0;
      }


      salida = PID_p + integral + PID_d;


      salida = map(salida, -150, 150, 0, 150);


      if (salida < 20) salida = 20;
      if (salida > 160) salida = 160;

      float angulo = salida + 30;
      servo.write(angulo);

      Serial.print("Distancia: ");
      Serial.print(distancia);
      Serial.print(" cm | Error: ");
      Serial.print(error);
      Serial.print(" | Salida PID: ");
      Serial.print(salida);
      Serial.print(" | Angulo Servo: ");
      Serial.println(angulo);
    }

    error_anterior = error;
  }

}
