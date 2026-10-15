import threading


class ZoomModeManager:
    """
    Gestiona el estado del modo
    de zoom controlado por cabeza.

    El modo inicia desactivado.
    """

    def __init__(self):

        self._enabled = False

        self._lock = (
            threading.RLock()
        )

    def enable(self):

        with self._lock:

            self._enabled = True

    def disable(self):

        with self._lock:

            self._enabled = False

    def set_enabled(
        self,
        enabled
    ):

        with self._lock:

            self._enabled = bool(
                enabled
            )

    def is_enabled(self):

        with self._lock:

            return self._enabled