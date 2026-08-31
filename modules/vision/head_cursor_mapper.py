class HeadCursorMapper:
    """
    Convierte los ángulos relativos de la cabeza
    en desplazamientos del cursor.
    """

    def __init__(
        self,
        sensitivity_x=2.0,
        sensitivity_y=2.0,
        dead_zone=2.0,
        max_step=30,
        smoothing=0.35
    ):
        self.sensitivity_x = sensitivity_x
        self.sensitivity_y = sensitivity_y
        self.dead_zone = dead_zone
        self.max_step = max_step
        self.smoothing = smoothing

        self.previous_dx = 0.0
        self.previous_dy = 0.0

    def _apply_dead_zone(self, value):

        if abs(value) <= self.dead_zone:
            return 0.0

        if value > 0:
            return value - self.dead_zone

        return value + self.dead_zone

    def _limit(self, value):

        return max(
            -self.max_step,
            min(self.max_step, value)
        )

    def calculate(
        self,
        yaw,
        pitch,
        neutral_yaw,
        neutral_pitch
    ):
        relative_yaw = yaw - neutral_yaw
        relative_pitch = pitch - neutral_pitch

        relative_yaw = self._apply_dead_zone(
            relative_yaw
        )

        relative_pitch = self._apply_dead_zone(
            relative_pitch
        )

        dx = relative_yaw * self.sensitivity_x
        dy = relative_pitch * self.sensitivity_y

        dx = self._limit(dx)
        dy = self._limit(dy)

        # Suavizado
        dx = (
            self.smoothing * dx
            + (1 - self.smoothing) * self.previous_dx
        )

        dy = (
            self.smoothing * dy
            + (1 - self.smoothing) * self.previous_dy
        )

        self.previous_dx = dx
        self.previous_dy = dy

        return int(dx), int(dy)

    def reset(self):

        self.previous_dx = 0.0
        self.previous_dy = 0.0