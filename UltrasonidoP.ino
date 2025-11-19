#define TRIG_PIN_1 9
#define ECHO_PIN_1 8
#define TRIG_PIN_2 7
#define ECHO_PIN_2 6

void setup() {
  Serial.begin(9600);
  
  pinMode(TRIG_PIN_1, OUTPUT);
  pinMode(ECHO_PIN_1, INPUT);
  pinMode(TRIG_PIN_2, OUTPUT);
  pinMode(ECHO_PIN_2, INPUT);
  
  Serial.println("Iniciando mediciones de ultrasonido...");
}

float medirDistancia(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  long duracion = pulseIn(echoPin, HIGH, 25000);
  float distancia = duracion * 0.0343 / 2;

  if (distancia == 0) {
    return -1.0;
  }
  return distancia;
}

void loop() {
  float dist1 = medirDistancia(TRIG_PIN_1, ECHO_PIN_1);
  delay(50);
  float dist2 = medirDistancia(TRIG_PIN_2, ECHO_PIN_2);

  Serial.print("Sensor 1: ");
  Serial.print(dist1, 2);
  Serial.print(" cm");
  
  Serial.print(" Sensor 2: ");
  Serial.print(dist2, 2);
  Serial.println(" cm");
  
  delay(500);
}
//RESPUESTAS DE DISTANCIAS

//
//Rango de lectura estable del sensor 2 cm 
//SETPOINT = 0.77 cm
//ZONA_MUERTA = 0.4 cm

//Sensor 1: 32.24 cm  Sensor 2: 31.45 cm
//Sensor 1: 32.34 cm  Sensor 2: 31.45 cm
//Sensor 1: 32.24 cm  Sensor 2: 31.57 cm
//Sensor 1: 32.24 cm  Sensor 2: 31.47 cm
//Sensor 1: 32.24 cm  Sensor 2: 31.45 cm
//Sensor 1: 32.24 cm  Sensor 2: 31.47 cm
//Sensor 1: 32.26 cm  Sensor 2: 31.47 cm
//Sensor 1: 32.24 cm  Sensor 2: 31.47 cm
//Sensor 1: 32.34 cm  Sensor 2: 31.57 cm
//Sensor 1: 32.24 cm  Sensor 2: 31.47 cm
//Sensor 1: 33.55 cm  Sensor 2: 31.47 cm
//Sensor 1: 33.55 cm  Sensor 2: 31.45 cm
//Sensor 1: 33.55 cm  Sensor 2: 31.47 cm