import winsound


class AudioFeedbackService:
    """
    Servicio de retroalimentación auditiva
    para ZeroUI-AC.

    Genera un tono breve después de una
    acción ejecutada correctamente.

    El servicio puede activarse o
    desactivarse mediante configuración.
    """

    def __init__(
        self,
        enabled=True,
        frequency=880,
        duration_ms=80
    ):

        self.enabled = (
            enabled
        )

        self.frequency = (
            frequency
        )

        self.duration_ms = (
            duration_ms
        )

    def set_enabled(
        self,
        enabled
    ):
        """
        Activa o desactiva
        la retroalimentación auditiva.
        """

        self.enabled = bool(
            enabled
        )

    def enable(self):
        """
        Activa el sonido.
        """

        self.enabled = True

    def disable(self):
        """
        Desactiva el sonido.
        """

        self.enabled = False

    def play_success(self):
        """
        Reproduce el tono de confirmación.

        Retorna True cuando el sonido
        pudo ejecutarse y False cuando
        está desactivado o ocurre un error.
        """

        if not self.enabled:

            return False

        try:

            winsound.Beep(
                self.frequency,
                self.duration_ms
            )

            return True

        except (
            RuntimeError,
            OSError
        ):

            return False