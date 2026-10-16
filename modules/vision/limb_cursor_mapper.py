class LimbCursorMapper:
    """
    Convierte la posición normalizada de la mano
    en coordenadas de pantalla.

    MediaPipe:
        X/Y entre aproximadamente 0.0 y 1.0

    Windows:
        X/Y en píxeles de pantalla
    """

    def __init__(
        self,
        margin=0.15,
        sensitivity_x=1.0,
        sensitivity_y=1.0,
        smoothing=0.35,
        min_movement=2
    ):
        self.margin = margin

        self.sensitivity_x = (
            sensitivity_x
        )

        self.sensitivity_y = (
            sensitivity_y
        )

        self.smoothing = smoothing

        self.min_movement = (
            min_movement
        )

        self.previous_x = None
        self.previous_y = None

    @staticmethod
    def _clamp(
        value,
        minimum,
        maximum
    ):
        return max(
            minimum,
            min(maximum, value)
        )

    def _normalize_with_margin(
        self,
        value
    ):
        """
        Convierte la zona útil de cámara
        al intervalo 0..1.
        """

        usable_area = (
            1.0 - 2.0 * self.margin
        )

        normalized = (
            value - self.margin
        ) / usable_area

        return self._clamp(
            normalized,
            0.0,
            1.0
        )

    @staticmethod
    def _apply_sensitivity(
        value,
        sensitivity
    ):
        """
        Aplica sensibilidad respecto
        al centro del movimiento.
        """

        centered = value - 0.5

        adjusted = (
            0.5
            + centered * sensitivity
        )

        return max(
            0.0,
            min(1.0, adjusted)
        )

    def calculate(
        self,
        hand_x,
        hand_y,
        screen_width,
        screen_height,
        sensitivity_factor=1.0
    ):
        """
        Convierte posición de muñeca
        en coordenadas absolutas de pantalla.
        """

        x = self._normalize_with_margin(
            hand_x
        )

        y = self._normalize_with_margin(
            hand_y
        )

        try:

            factor = float(
                sensitivity_factor
            )

        except (
            TypeError,
            ValueError
        ):

            factor = 1.0


        if factor <= 0.0:
            factor = 1.0


        effective_sensitivity_x = (
            self.sensitivity_x
            * factor
        )

        effective_sensitivity_y = (
            self.sensitivity_y
            * factor
        )


        x = self._apply_sensitivity(
            x,
            effective_sensitivity_x
        )

        y = self._apply_sensitivity(
            y,
            effective_sensitivity_y
        )

        target_x = (
            x * (screen_width - 1)
        )

        target_y = (
            y * (screen_height - 1)
        )

        if self.previous_x is None:

            self.previous_x = target_x
            self.previous_y = target_y

        smooth_x = (
            self.smoothing * target_x
            + (1 - self.smoothing)
            * self.previous_x
        )

        smooth_y = (
            self.smoothing * target_y
            + (1 - self.smoothing)
            * self.previous_y
        )

        if (
            abs(
                smooth_x
                - self.previous_x
            )
            < self.min_movement
        ):
            smooth_x = self.previous_x

        if (
            abs(
                smooth_y
                - self.previous_y
            )
            < self.min_movement
        ):
            smooth_y = self.previous_y

        self.previous_x = smooth_x
        self.previous_y = smooth_y

        return (
            int(smooth_x),
            int(smooth_y)
        )

    def reset(self):
        self.previous_x = None
        self.previous_y = None