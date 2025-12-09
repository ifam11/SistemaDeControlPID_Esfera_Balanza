class PID:
    def __init__(self, kp, ki, kd, setpoint):

        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.prev_error = 0
        self.integral = 0

    def reset(self):
        self.error_prev = 0.0
        self.integral = 0.0

    def calcular(self, medicion_cm, dt):
        error = self.setpoint - medicion_cm

        self.integral += error * dt
        self.integral = max(min(self.integral, 15.0), -15.0)

        derivada = (error - self.error_prev) / dt if dt > 0 else 0.0
        self.error_prev = error

        return (self.kp * error) + (self.ki * self.integral) + (self.kd * derivada)
 #COMPLETO 