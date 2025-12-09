class PID:
    def __init__(self, kp, ki, kd, setpoint):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.error_prev = 0.0
        self.integral = 0.0

    def reset(self):
        self.error_prev = 0.0
        self.integral = 0.0

    def calcular(self, setpoint, medicion_cm, dt):
        error = setpoint - medicion_cm
        self.integral += error * dt

        derivada = (error - self.prev_error) / dt if dt > 0 else 0
        self.prev_error = error

        return (self.kp * error) + (self.ki * self.integral) + (self.kd * derivada)
