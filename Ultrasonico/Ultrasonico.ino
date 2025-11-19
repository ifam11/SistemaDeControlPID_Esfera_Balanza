#include <Servo.h>

#define TRIG_PIN 9 
#define ECHO_PIN 8 
const int SERVO_PIN = 10;

const float DISTANCE_SETPOINT = 15.71;
const int SERVO_NEUTRAL_ANGLE = 65;
const int SERVO_LIMITE_MIN = 25;
const int SERVO_LIMITE_MAX = 140;

float kp = 3.5;
float kd = 350.0;

float ki = 0.2;

Servo myservo;
float distance = 0.0;
unsigned long time;
float distance_previous_error, distance_error;
int period = 40;
float PID_p, PID_i, PID_d, PID_total;

float medirDistanciaFiltrada() { 
  const int muestras = 5;
  float suma = 0;
  int validas = 0;
  for (int i = 0; i < muestras; i++) {
    digitalWrite(TRIG_PIN, LOW); delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);
    long duracion = pulseIn(ECHO_PIN, HIGH, 25000); // Timeout de 25ms
    if (duracion > 0) { 
      suma += (duracion * 0.0343) / 2.0;
      validas++;
    }
    delay(5);
  }
  return (validas > 0) ? (suma / validas) : -1.0;
}

void setup() {
  Serial.begin(115200);  
  myservo.attach(SERVO_PIN);
  myservo.write(SERVO_NEUTRAL_ANGLE);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  time = millis();
}

void loop() {
  if (millis() > time + period) {
    time = millis();    
    distance = medirDistanciaFiltrada();

    if (distance < 0 || distance > 30) {
      myservo.write(SERVO_NEUTRAL_ANGLE);
      PID_i = 0;
      distance_previous_error = 0;
      return;
    }
    
    // --- Cálculo PID ---
    distance_error = DISTANCE_SETPOINT - distance;   
    PID_p = kp * distance_error;
    PID_d = kd * ((distance_error - distance_previous_error) / period);
      
    if (-3.5 < distance_error && distance_error < 3.5) { // Ampliamos un poco el rango para que actúe
      PID_i = PID_i + (ki * distance_error);
    } else {
      PID_i = 0;
    }
  
    PID_total = PID_p + PID_i + PID_d;  

    int angulo = SERVO_NEUTRAL_ANGLE - PID_total;

    if (angulo < SERVO_LIMITE_MIN) angulo = SERVO_LIMITE_MIN;
    if (angulo > SERVO_LIMITE_MAX) angulo = SERVO_LIMITE_MAX;
  
    myservo.write(angulo);  
    distance_previous_error = distance_error;

    Serial.print("Dist: "); Serial.print(distance, 2);
    Serial.print(" | Err: "); Serial.print(distance_error, 2);
    Serial.print(" | Ang: "); Serial.println(angulo);
  }
}