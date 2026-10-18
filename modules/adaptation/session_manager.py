import threading

from datetime import (
    datetime,
    timezone
)

from uuid import uuid4

from modules.adaptation.session_metrics import (
    SessionMetrics
)

from modules.adaptation.fatigue_estimator import (
    FatigueEstimator
)


class SessionManager:
    """
    Gestiona el ciclo de vida de una
    sesión de uso de ZeroUI-AC.

    Puede persistir el resumen final
    mediante un componente inyectado.
    """

    def __init__(
        self,
        persistence=None,
        fatigue_estimator=None
    ):

        self._lock = (
            threading.RLock()
        )

        self._active = False

        self._session_id = None
        self._started_at = None

        self._metrics = None

        self._last_summary = None

        self._persistence = (
            persistence
        )

        self._fatigue_estimator = (
            fatigue_estimator
            or FatigueEstimator()
        )

        self._last_persistence_error = (
            None
        )

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

            self._last_persistence_error = (
                None
            )

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

    def _estimate_fatigue(
        self,
        metrics_snapshot
    ):
        """
        Obtiene el estado operativo
        de fatiga de forma segura.

        Una falla del estimador no debe
        impedir cerrar la sesión.
        """

        try:

            estimate = (
                self._fatigue_estimator
                .estimate(
                    metrics_snapshot
                )
            )

            return {
                "score":
                    estimate.score,

                "level":
                    estimate.level,

                "components": {

                    "duration":
                        estimate
                        .duration_component,

                    "voice_error":
                        estimate
                        .voice_error_component,

                    "action_interval":
                        estimate
                        .action_interval_component,

                    "movement":
                        estimate
                        .movement_component,

                    "switching":
                        estimate
                        .switching_component,
                }
            }

        except Exception:

            return {
                "score": None,

                "level":
                    "unavailable",

                "components": {}
            }

    def end_session(self):
        """
        Finaliza la sesión activa,
        calcula el índice operativo
        de fatiga y persiste el resumen
        cuando existe almacenamiento
        configurado.
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

            metrics_snapshot = (
                self._metrics
                .snapshot()
            )

            fatigue = (
                self._estimate_fatigue(
                    metrics_snapshot
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
                    metrics_snapshot,

                "fatigue":
                    fatigue,
            }

            self._last_summary = (
                summary
            )

            self._active = False

            self._session_id = None
            self._started_at = None
            self._metrics = None

            persistence = (
                self._persistence
            )

        # La escritura a disco se realiza
        # después de liberar el lock de sesión.
        if persistence is not None:

            try:

                persistence.save(
                    summary
                )

                with self._lock:

                    self._last_persistence_error = (
                        None
                    )

            except Exception as error:

                # Un problema de disco nunca
                # debe impedir finalizar
                # correctamente la sesión.
                with self._lock:

                    self._last_persistence_error = (
                        f"{type(error).__name__}: "
                        f"{error}"
                    )

        return summary

    def get_last_summary(self):

        with self._lock:

            return (
                self._last_summary
            )

    def get_last_persistence_error(
        self
    ):

        with self._lock:

            return (
                self._last_persistence_error
            )