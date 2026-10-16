import math
import threading
import time

from domain.events.event_types import (
    EventSource,
    EventType
)


class SessionMetrics:
    """
    Acumula métricas operativas durante
    una sesión de ZeroUI-AC.

    No ejecuta acciones sobre Windows.
    """

    USER_SOURCES = (
        EventSource.VOICE,
        EventSource.HEAD,
        EventSource.LIMB,
        EventSource.GESTURE,
    )

    def __init__(self):

        self._lock = (
            threading.RLock()
        )

        self.started_at = (
            time.monotonic()
        )

        self.total_events = 0

        self.action_events = 0
        self.cursor_events = 0

        self.error_events = 0

        # Errores específicamente
        # originados por el canal de voz.
        self.voice_error_events = 0

        self.source_counts = {
            EventSource.VOICE: 0,
            EventSource.HEAD: 0,
            EventSource.LIMB: 0,
            EventSource.GESTURE: 0,
            EventSource.SYSTEM: 0,
        }

        # Conserva la métrica histórica:
        # cualquier cambio de fuente.
        self.channel_switches = 0

        # Cambios solamente entre
        # modalidades utilizadas
        # directamente por el usuario.
        self.user_channel_switches = 0

        self._last_source = None
        self._last_user_source = None

        # Intervalos entre acciones.
        self._last_action_timestamp = None

        self._action_interval_sum = 0.0
        self._action_interval_samples = 0

        # Estadística incremental de
        # magnitud de movimiento.
        self._movement_samples = 0

        self._movement_mean = 0.0
        self._movement_m2 = 0.0

        # Posición previa para movimientos
        # absolutos de la extremidad.
        self._last_absolute_cursor = {}

    def _record_action_interval(
        self,
        event
    ):
        """
        Registra el intervalo entre
        acciones consecutivas.
        """

        try:

            timestamp = float(
                event.timestamp
            )

        except (
            TypeError,
            ValueError,
            AttributeError
        ):

            return

        if not math.isfinite(
            timestamp
        ):

            return

        if (
            self._last_action_timestamp
            is None
        ):

            self._last_action_timestamp = (
                timestamp
            )

            return

        if (
            timestamp
            < self._last_action_timestamp
        ):

            return

        interval = (
            timestamp
            - self._last_action_timestamp
        )

        self._action_interval_sum += (
            interval
        )

        self._action_interval_samples += 1

        self._last_action_timestamp = (
            timestamp
        )

    def _record_movement_sample(
        self,
        magnitude
    ):
        """
        Actualiza media y variabilidad
        del movimiento mediante cálculo
        incremental.
        """

        try:

            magnitude = float(
                magnitude
            )

        except (
            TypeError,
            ValueError
        ):

            return

        if not math.isfinite(
            magnitude
        ):

            return

        if magnitude < 0.0:
            return

        self._movement_samples += 1

        delta = (
            magnitude
            - self._movement_mean
        )

        self._movement_mean += (
            delta
            / self._movement_samples
        )

        delta_2 = (
            magnitude
            - self._movement_mean
        )

        self._movement_m2 += (
            delta
            * delta_2
        )

    def _record_cursor_movement(
        self,
        event
    ):
        """
        Obtiene una magnitud comparable
        del movimiento del cursor.

        Cabeza:
            desplazamiento relativo.

        Extremidad:
            diferencia entre posiciones
            absolutas consecutivas.
        """

        payload = (
            event.payload
            or {}
        )

        mode = payload.get(
            "mode"
        )

        if mode == "relative":

            try:

                dx = float(
                    payload.get(
                        "dx",
                        0.0
                    )
                )

                dy = float(
                    payload.get(
                        "dy",
                        0.0
                    )
                )

            except (
                TypeError,
                ValueError
            ):

                return

            magnitude = math.hypot(
                dx,
                dy
            )

            self._record_movement_sample(
                magnitude
            )

            return

        if mode == "absolute":

            try:

                x = float(
                    payload.get("x")
                )

                y = float(
                    payload.get("y")
                )

            except (
                TypeError,
                ValueError
            ):

                return

            if (
                not math.isfinite(x)
                or not math.isfinite(y)
            ):

                return

            previous = (
                self._last_absolute_cursor
                .get(
                    event.source
                )
            )

            self._last_absolute_cursor[
                event.source
            ] = (
                x,
                y
            )

            if previous is None:
                return

            previous_x, previous_y = (
                previous
            )

            magnitude = math.hypot(
                x - previous_x,
                y - previous_y
            )

            self._record_movement_sample(
                magnitude
            )

    def record_event(
        self,
        event
    ):
        """
        Registra un InteractionEvent
        procesado por el sistema.
        """

        if event is None:
            return

        with self._lock:

            self.total_events += 1

            source = (
                event.source
            )

            if (
                source
                in self.source_counts
            ):

                self.source_counts[
                    source
                ] += 1

            if (
                event.event_type
                == EventType.ACTION
            ):

                self.action_events += 1

                self._record_action_interval(
                    event
                )

            elif (
                event.event_type
                == EventType.CURSOR_MOVE
            ):

                self.cursor_events += 1

                self._record_cursor_movement(
                    event
                )

            elif (
                event.event_type
                == EventType.STATUS
            ):

                payload = (
                    event.payload
                    or {}
                )

                if (
                    payload.get("level")
                    == "error"
                ):

                    self.error_events += 1

                    if (
                        source
                        == EventSource.VOICE
                    ):

                        self.voice_error_events += 1

            # Métrica histórica:
            # cualquier cambio de fuente.
            if (
                self._last_source
                is not None
                and source
                != self._last_source
            ):

                self.channel_switches += 1

            self._last_source = (
                source
            )

            # Métrica útil para fatiga:
            # solamente canales del usuario.
            if (
                source
                in self.USER_SOURCES
            ):

                if (
                    self._last_user_source
                    is not None
                    and source
                    != self._last_user_source
                ):

                    self.user_channel_switches += 1

                self._last_user_source = (
                    source
                )

    def get_duration(
        self
    ):

        with self._lock:

            return max(
                0.0,
                time.monotonic()
                - self.started_at
            )

    def get_source_count(
        self,
        source
    ):

        with self._lock:

            return (
                self.source_counts
                .get(
                    source,
                    0
                )
            )

    def get_error_rate(
        self
    ):

        with self._lock:

            if self.total_events == 0:
                return 0.0

            return (
                self.error_events
                / self.total_events
            )

    def get_voice_error_rate(
        self
    ):

        with self._lock:

            voice_events = (
                self.source_counts.get(
                    EventSource.VOICE,
                    0
                )
            )

            if voice_events == 0:
                return 0.0

            return min(
                1.0,
                self.voice_error_events
                / voice_events
            )

    def get_average_action_interval(
        self
    ):

        with self._lock:

            if (
                self._action_interval_samples
                == 0
            ):

                return 0.0

            return (
                self._action_interval_sum
                / self._action_interval_samples
            )

    def get_average_movement_magnitude(
        self
    ):

        with self._lock:

            if self._movement_samples == 0:
                return 0.0

            return self._movement_mean

    def get_movement_variability(
        self
    ):
        """
        Devuelve la desviación estándar
        poblacional de la magnitud de
        los movimientos registrados.
        """

        with self._lock:

            if self._movement_samples < 2:
                return 0.0

            variance = (
                self._movement_m2
                / self._movement_samples
            )

            return math.sqrt(
                max(
                    0.0,
                    variance
                )
            )

    def snapshot(
        self
    ):
        """
        Devuelve una copia estable
        de las métricas actuales.
        """

        with self._lock:

            return {
                "duration_seconds":
                    self.get_duration(),

                "total_events":
                    self.total_events,

                "action_events":
                    self.action_events,

                "cursor_events":
                    self.cursor_events,

                "error_events":
                    self.error_events,

                "error_rate":
                    self.get_error_rate(),

                "voice_error_events":
                    self.voice_error_events,

                "voice_error_rate":
                    self.get_voice_error_rate(),

                "channel_switches":
                    self.channel_switches,

                "user_channel_switches":
                    self.user_channel_switches,

                "average_action_interval_seconds":
                    self.get_average_action_interval(),

                "action_interval_samples":
                    self._action_interval_samples,

                "average_movement_magnitude":
                    self.get_average_movement_magnitude(),

                "movement_variability":
                    self.get_movement_variability(),

                "movement_samples":
                    self._movement_samples,

                "source_counts": {
                    source.value: count
                    for source, count
                    in self.source_counts.items()
                }
            }