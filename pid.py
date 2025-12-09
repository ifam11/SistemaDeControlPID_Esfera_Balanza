class ControladorPID:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def calcular(self, setpoint, valor_actual, dt):
        error = setpoint - valor_actual
        self.integral += error * dt

        derivative = (error - self.prev_error) / dt if dt > 0 else 0
        self.prev_error = error

        salida = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        return salida
