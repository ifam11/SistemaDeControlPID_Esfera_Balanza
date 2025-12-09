class ControladorPID:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.error_prev = 0.0
        self.integral = 0.0

    def reset(self):
        self.error_prev = 0.0
        self.integral = 0.0

    def calcular(self, medicion_cm, dt):
        error = self.setpoint - medicion_cm

    def calcular(self, setpoint, valor_actual, dt):
        error = setpoint - valor_actual
        self.integral += error * dt

        derivative = (error - self.prev_error) / dt if dt > 0 else 0
        self.prev_error = error

        salida = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        return salida
