#include <Servo.h>

#define TRIG_PIN 9 
#define ECHO_PIN 8 
const int SERVO_PIN = 10;

float setpoint = 15.0;  


float distancia = 0;
float error = 0;
float error_anterior = 0;
float integral = 0;
float derivada = 0;
float salida = 0;


float Kp = 8;     
float Ki = 0.2;   
float Kd = 5;  


unsigned long tiempo_anterior = 0;
const unsigned long periodo = 50; 

Servo servo;


#define Habilitar_Telemetria true
unsigned long UltimoChequeoSerial = 0;
unsigned long UltimaEnvioTelemetria = 0;
bool TelemetriaActiva = true;


void ImprimirTelemetria() {
  Serial.println(F("---MODO TELEMETRIA ACTIVADO---"));
  Serial.println(F("Comandos disponibles: "));
  Serial.println(F("P<valor> = cambia Kp (Ej: P7.5)"));
  Serial.println(F("I<valor> = cambia Ki (Ej: I0.3)"));
  Serial.println(F("D<valor> = cambia Kd (Ej: D5)"));
  Serial.println(F("S = mostrar valores actuales"));
  Serial.println(F("L = activar/desactivar telemetría"));
}

void ProcesarComandosSerial() {
  if (millis() - UltimoChequeoSerial < 100) return;
  UltimoChequeoSerial = millis();

  while (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();
    if (comando.length() == 0) continue;

    char codigoComando = toupper(comando.charAt(0));
    String valorTexto = comando.substring(1);

    switch (codigoComando) {
      case 'P':
        Kp = valorTexto.toFloat();
        Serial.print(F("Nuevo Kp = "));
        Serial.println(Kp);
        break;
      case 'I':
        Ki = valorTexto.toFloat();
        Serial.print(F("Nuevo Ki = "));
        Serial.println(Ki);
        break;
      case 'D':
        Kd = valorTexto.toFloat();
        Serial.print(F("Nuevo Kd = "));
        Serial.println(Kd);
        break;
      case 'S':
        Serial.print(F("Kp=")); Serial.print(Kp);
        Serial.print(F(" Ki=")); Serial.print(Ki);
        Serial.print(F(" Kd=")); Serial.println(Kd);
        break;
      case 'L':
        TelemetriaActiva = !TelemetriaActiva;
        Serial.print(F("Telemetría "));
        Serial.println(TelemetriaActiva ? F("ACTIVADA") : F("DESACTIVADA"));
        break;
      default:
        Serial.print(F("Comando no reconocido: "));
        Serial.println(comando);
    }
  }
}


void EnviarTelemetria(float distancia, float setpoint, float salida) {
  if (!Habilitar_Telemetria || !TelemetriaActiva) return;
  if (millis() - UltimaEnvioTelemetria < 200) return;
  UltimaEnvioTelemetria = millis();

  Serial.print("Tiempo = "); Serial.print(millis());
  Serial.print(" ms | Distancia = "); Serial.print(distancia);
  Serial.print(" cm | Setpoint = "); Serial.print(setpoint);
  Serial.print(" cm | Salida PID = "); Serial.print(salida);
  Serial.print(" | Kp="); Serial.print(Kp);
  Serial.print(" Ki="); Serial.print(Ki);
  Serial.print(" Kd="); Serial.println(Kd);
}


float medirDistancia() { 
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
    if (duracion > 0) {
      float d = duracion * 0.034 / 2;
      suma += d;
      validas++;
    }
    delay(5); 
  }

  return validas > 0 ? suma / validas : -1;
}


void setup() {
  Serial.begin(9600);
  servo.attach(SERVO_PIN);
  servo.write(90); 

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  Serial.println("==============================================");
  Serial.println(" SISTEMA DE CONTROL PID - BALANZA Y ESFERA ");
  Serial.println("==============================================");
  Serial.println("Iniciando sistema...");
  Serial.println();

  ImprimirTelemetria();
}


void loop() {
  ProcesarComandosSerial();

  unsigned long ahora = millis();
  float dt = (ahora - tiempo_anterior) / 1000.0; 

  if (dt >= periodo / 1000.0) {
    tiempo_anterior = ahora;
    distancia = medirDistancia();

    if (distancia == -1 || distancia > 30) {
      servo.write(90); 
      Serial.println("[INFO] Objeto no detectado o fuera de rango. Servo en posición neutra.");
      return;
    }


    error = setpoint - distancia;
    integral += Ki * error * dt;
    integral = constrain(integral, -50, 50);
    derivada = (error - error_anterior) / dt;

    salida = Kp * error + integral + Kd * derivada;
    salida = constrain(salida, 20, 160);

    float angulo = constrain(salida + 30, 0, 180);
    servo.write(angulo);

 
    error_anterior = error;

    EnviarTelemetria(distancia, setpoint, salida);

    
    Serial.println("----------------------------------------------");
    Serial.print("Tiempo actual: "); Serial.print(ahora / 1000.0, 2); Serial.println(" s");
    Serial.print("Distancia medida: "); Serial.print(distancia, 2); Serial.println(" cm");
    Serial.print("Error actual: "); Serial.println(error, 2);
    Serial.print("Componente P: "); Serial.println(Kp * error, 2);
    Serial.print("Componente I: "); Serial.println(integral, 2);
    Serial.print("Componente D: "); Serial.println(Kd * derivada, 2);
    Serial.print("Salida PID total: "); Serial.println(salida, 2);
    Serial.print("Ángulo aplicado al servo: "); Serial.println(angulo, 2);
    Serial.println("----------------------------------------------");
  }
}