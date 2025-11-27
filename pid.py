class ControladorPID:
    def __init__(self, kp, ki, kd, output_limits=(None, None), integral_limit=None, deriv_filter_alpha=0.0):
        """
        Inicializa el controlador con las ganancias Proporcional, Integral y Derivativa.
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0
        self.prev_derivative = 0.0

        self.min_output, self.max_output = output_limits
        self.integral_limit = integral_limit
        self.alpha = float(deriv_filter_alpha)

    def reset(self):
        self.prev_error = 0.0
        self.integral = 0.0
        self.prev_derivative = 0.0

    def calcular(self, setpoint, valor_actual, dt):
        """
        Calcula la salida del control basándose en el error y el tiempo transcurrido (dt).
        """
        error = setpoint - valor_actual
        self.integral += error * dt
        
        if self.integral_limit is not None:
                    if self.integral > self.integral_limit:
                        self.integral = self.integral_limit
                    elif self.integral < -self.integral_limit:
                        self.integral = -self.integral_limit

         # Derivada (filtrada)
        raw_derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
        derivative = (self.alpha * self.prev_derivative) + ((1.0 - self.alpha) * raw_derivative)
        self.prev_derivative = derivative
        self.prev_error = error

        salida = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)

        # Limitación de salida
        if (self.max_output is not None) and (salida > self.max_output):
            salida = self.max_output
        if (self.min_output is not None) and (salida < self.min_output):
            salida = self.min_output

        return salida