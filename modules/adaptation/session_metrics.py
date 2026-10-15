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

        self.source_counts = {
            EventSource.VOICE: 0,
            EventSource.HEAD: 0,
            EventSource.LIMB: 0,
            EventSource.GESTURE: 0,
            EventSource.SYSTEM: 0,
        }

        self.channel_switches = 0

        self._last_source = None

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

            elif (
                event.event_type
                == EventType.CURSOR_MOVE
            ):

                self.cursor_events += 1

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
                self._last_source
                is not None
                and source
                != self._last_source
            ):

                self.channel_switches += 1

            self._last_source = (
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

                "channel_switches":
                    self.channel_switches,

                "source_counts": {
                    source.value: count
                    for source, count
                    in self.source_counts.items()
                }
            }