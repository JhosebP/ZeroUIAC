from dataclasses import dataclass


@dataclass(frozen=True)
class AdaptiveState:
    """
    Representa un estado discreto y estable
    para el futuro agente adaptativo.
    """

    voice_error_level: str
    activity_level: str
    switch_level: str
    dominant_source: str
    session_stage: str

    def as_key(self):
        """
        Devuelve una clave hashable para
        utilizar posteriormente en la Q-table.
        """

        return (
            self.voice_error_level,
            self.activity_level,
            self.switch_level,
            self.dominant_source,
            self.session_stage,
        )


class AdaptiveStateBuilder:
    """
    Convierte las métricas continuas de una
    sesión en un estado discreto.

    No modifica parámetros del sistema
    ni ejecuta acciones sobre Windows.
    """

    SOURCE_KEYS = (
        "voice",
        "head",
        "limb",
        "gesture",
    )

    def __init__(
        self,
        error_low_max=0.10,
        error_medium_max=0.30,
        activity_low_max=2.0,
        activity_medium_max=6.0,
        switch_low_max=2.0,
        switch_medium_max=8.0,
        dominance_ratio=0.60,
        short_session_max=600.0,
        medium_session_max=1800.0,
    ):

        self.error_low_max = error_low_max
        self.error_medium_max = error_medium_max

        self.activity_low_max = activity_low_max
        self.activity_medium_max = activity_medium_max

        self.switch_low_max = switch_low_max
        self.switch_medium_max = switch_medium_max

        self.dominance_ratio = dominance_ratio

        self.short_session_max = short_session_max
        self.medium_session_max = medium_session_max

    def _rate_per_minute(
        self,
        count,
        duration_seconds,
    ):
        """
        Calcula una tasa por minuto.

        Durante el primer minuto utiliza una
        ventana mínima de 60 segundos para
        evitar estados extremadamente variables
        al comenzar una sesión.
        """

        duration = max(
            float(duration_seconds),
            60.0,
        )

        return (
            float(count)
            * 60.0
            / duration
        )

    def _classify_error(
        self,
        error_rate,
    ):

        if error_rate <= self.error_low_max:
            return "low"

        if error_rate <= self.error_medium_max:
            return "medium"

        return "high"

    def _classify_activity(
        self,
        actions_per_minute,
    ):

        if (
            actions_per_minute
            < self.activity_low_max
        ):
            return "low"

        if (
            actions_per_minute
            < self.activity_medium_max
        ):
            return "medium"

        return "high"

    def _classify_switches(
        self,
        switches_per_minute,
    ):

        if (
            switches_per_minute
            < self.switch_low_max
        ):
            return "low"

        if (
            switches_per_minute
            < self.switch_medium_max
        ):
            return "medium"

        return "high"

    def _get_dominant_source(
        self,
        source_counts,
    ):

        counts = {
            source: max(
                0,
                int(
                    source_counts.get(
                        source,
                        0,
                    )
                    or 0
                ),
            )
            for source
            in self.SOURCE_KEYS
        }

        total = sum(
            counts.values()
        )

        if total == 0:
            return "none"

        source, count = max(
            counts.items(),
            key=lambda item: item[1],
        )

        ratio = (
            count
            / total
        )

        if (
            ratio
            >= self.dominance_ratio
        ):
            return source

        return "mixed"

    def _get_session_stage(
        self,
        duration_seconds,
    ):

        if (
            duration_seconds
            < self.short_session_max
        ):
            return "short"

        if (
            duration_seconds
            < self.medium_session_max
        ):
            return "medium"

        return "long"

    def build(
        self,
        snapshot,
    ):
        """
        Construye un AdaptiveState.

        Puede recibir directamente el snapshot
        de SessionManager o solo el diccionario
        de métricas.
        """

        if snapshot is None:
            snapshot = {}

        metrics = (
            snapshot.get(
                "metrics",
                snapshot,
            )
            or {}
        )

        duration = max(
            0.0,
            float(
                metrics.get(
                    "duration_seconds",
                    0.0,
                )
                or 0.0
            ),
        )

        action_events = max(
            0,
            int(
                metrics.get(
                    "action_events",
                    0,
                )
                or 0
            ),
        )

        error_events = max(
            0,
            int(
                metrics.get(
                    "error_events",
                    0,
                )
                or 0
            ),
        )

        voice_error_events = max(
            0,
            int(
                metrics.get(
                    "voice_error_events",
                    error_events,
                )
                or 0
            ),
        )

        channel_switches = max(
            0,
            int(
                metrics.get(
                    "user_channel_switches",
                    metrics.get(
                        "channel_switches",
                        0,
                    ),
                )
                or 0
            ),
        )

        source_counts = (
            metrics.get(
                "source_counts",
                {},
            )
            or {}
        )

        voice_events = max(
            0,
            int(
                source_counts.get(
                    "voice",
                    0,
                )
                or 0
            ),
        )

        if voice_events == 0:
            voice_error_rate = 0.0
        else:
            voice_error_rate = min(
                1.0,
                voice_error_events
                / voice_events,
            )

        actions_per_minute = (
            self._rate_per_minute(
                action_events,
                duration,
            )
        )

        switches_per_minute = (
            self._rate_per_minute(
                channel_switches,
                duration,
            )
        )

        return AdaptiveState(
            voice_error_level=(
                self._classify_error(
                    voice_error_rate
                )
            ),
            activity_level=(
                self._classify_activity(
                    actions_per_minute
                )
            ),
            switch_level=(
                self._classify_switches(
                    switches_per_minute
                )
            ),
            dominant_source=(
                self._get_dominant_source(
                    source_counts
                )
            ),
            session_stage=(
                self._get_session_stage(
                    duration
                )
            ),
        )