import threading
from datetime import (
    datetime,
    timezone
)
from uuid import uuid4

from modules.adaptation.session_metrics import (
    SessionMetrics
)


class SessionManager:
    """
    Gestiona el ciclo de vida de una
    sesión de uso de ZeroUI-AC.
    """

    def __init__(self):

        self._lock = (
            threading.RLock()
        )

        self._active = False

        self._session_id = None
        self._started_at = None

        self._metrics = None

        self._last_summary = None

    @property
    def is_active(self):

        with self._lock:

            return self._active

    @property
    def session_id(self):

        with self._lock:

            return self._session_id

    def start_session(self):
        """
        Inicia una nueva sesión.

        Si ya existe una sesión activa,
        devuelve su identificador actual.
        """

        with self._lock:

            if self._active:

                return (
                    self._session_id
                )

            self._session_id = (
                str(uuid4())
            )

            self._started_at = (
                datetime.now(
                    timezone.utc
                )
            )

            self._metrics = (
                SessionMetrics()
            )

            self._active = True

            return (
                self._session_id
            )

    def record_event(
        self,
        event
    ):
        """
        Registra un evento únicamente
        cuando existe una sesión activa.
        """

        with self._lock:

            if (
                not self._active
                or self._metrics
                is None
            ):

                return False

            self._metrics.record_event(
                event
            )

            return True

    def get_snapshot(self):
        """
        Devuelve el estado actual
        de la sesión activa.
        """

        with self._lock:

            if (
                not self._active
                or self._metrics
                is None
            ):

                return None

            return {
                "session_id":
                    self._session_id,

                "started_at":
                    self._started_at
                    .isoformat(),

                "metrics":
                    self._metrics
                    .snapshot()
            }

    def end_session(self):
        """
        Finaliza la sesión activa y
        devuelve su resumen completo.
        """

        with self._lock:

            if (
                not self._active
                or self._metrics
                is None
            ):

                return None

            ended_at = (
                datetime.now(
                    timezone.utc
                )
            )

            summary = {
                "session_id":
                    self._session_id,

                "started_at":
                    self._started_at
                    .isoformat(),

                "ended_at":
                    ended_at
                    .isoformat(),

                "metrics":
                    self._metrics
                    .snapshot()
            }

            self._last_summary = (
                summary
            )

            self._active = False
            self._session_id = None
            self._started_at = None
            self._metrics = None

            return summary

    def get_last_summary(self):

        with self._lock:

            return (
                self._last_summary
            )