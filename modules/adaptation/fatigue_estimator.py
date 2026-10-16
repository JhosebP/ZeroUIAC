import math

from dataclasses import dataclass


@dataclass(frozen=True)
class FatigueEstimate:
    """
    Resultado estable de la estimación
    operativa de fatiga.
    """

    score: float
    level: str

    duration_component: float
    voice_error_component: float
    action_interval_component: float
    movement_component: float
    switching_component: float


class FatigueEstimator:
    """
    Estima un índice operativo de fatiga
    a partir de patrones de interacción.

    No representa un diagnóstico médico.

    El resultado se encuentra entre:

        0.0 = mínima evidencia operativa
        1.0 = máxima evidencia operativa
    """

    DURATION_WEIGHT = 0.25
    VOICE_ERROR_WEIGHT = 0.20
    ACTION_INTERVAL_WEIGHT = 0.20
    MOVEMENT_WEIGHT = 0.20
    SWITCHING_WEIGHT = 0.15

    LOW_MAX = 0.35
    MEDIUM_MAX = 0.65

    def __init__(
        self,
        duration_low=900.0,
        duration_high=3600.0,
        voice_error_low=0.10,
        voice_error_high=0.40,
        action_interval_low=2.0,
        action_interval_high=8.0,
        movement_variability_low=0.20,
        movement_variability_high=1.00,
        switching_low=2.0,
        switching_high=8.0,
    ):

        self.duration_low = (
            duration_low
        )

        self.duration_high = (
            duration_high
        )

        self.voice_error_low = (
            voice_error_low
        )

        self.voice_error_high = (
            voice_error_high
        )

        self.action_interval_low = (
            action_interval_low
        )

        self.action_interval_high = (
            action_interval_high
        )

        self.movement_variability_low = (
            movement_variability_low
        )

        self.movement_variability_high = (
            movement_variability_high
        )

        self.switching_low = (
            switching_low
        )

        self.switching_high = (
            switching_high
        )

    @staticmethod
    def _safe_float(
        value,
        default=0.0
    ):

        try:

            value = float(
                value
            )

        except (
            TypeError,
            ValueError
        ):

            return default

        if not math.isfinite(
            value
        ):

            return default

        return value

    @staticmethod
    def _clamp(
        value,
        minimum=0.0,
        maximum=1.0
    ):

        return max(
            minimum,
            min(
                maximum,
                value
            )
        )

    def _normalize(
        self,
        value,
        low,
        high
    ):
        """
        Normaliza linealmente una señal
        al intervalo 0..1.
        """

        value = self._safe_float(
            value
        )

        low = self._safe_float(
            low
        )

        high = self._safe_float(
            high,
            default=1.0
        )

        if high <= low:
            return 0.0

        if value <= low:
            return 0.0

        if value >= high:
            return 1.0

        return (
            value - low
        ) / (
            high - low
        )

    def _classify(
        self,
        score
    ):

        if score < self.LOW_MAX:
            return "low"

        if score < self.MEDIUM_MAX:
            return "medium"

        return "high"

    def estimate(
        self,
        snapshot
    ):
        """
        Puede recibir directamente
        las métricas o el snapshot
        completo de SessionManager.
        """

        if snapshot is None:
            snapshot = {}

        metrics = (
            snapshot.get(
                "metrics",
                snapshot
            )
            or {}
        )

        duration = max(
            0.0,
            self._safe_float(
                metrics.get(
                    "duration_seconds",
                    0.0
                )
            )
        )

        voice_error_rate = (
            self._clamp(
                self._safe_float(
                    metrics.get(
                        "voice_error_rate",
                        0.0
                    )
                )
            )
        )

        action_interval = max(
            0.0,
            self._safe_float(
                metrics.get(
                    "average_action_interval_seconds",
                    0.0
                )
            )
        )

        action_interval_samples = max(
            0,
            int(
                self._safe_float(
                    metrics.get(
                        "action_interval_samples",
                        0
                    )
                )
            )
        )

        average_movement = max(
            0.0,
            self._safe_float(
                metrics.get(
                    "average_movement_magnitude",
                    0.0
                )
            )
        )

        movement_variability = max(
            0.0,
            self._safe_float(
                metrics.get(
                    "movement_variability",
                    0.0
                )
            )
        )

        movement_samples = max(
            0,
            int(
                self._safe_float(
                    metrics.get(
                        "movement_samples",
                        0
                    )
                )
            )
        )

        user_switches = max(
            0,
            int(
                self._safe_float(
                    metrics.get(
                        "user_channel_switches",
                        0
                    )
                )
            )
        )

        source_counts = (
            metrics.get(
                "source_counts",
                {}
            )
            or {}
        )

        voice_events = max(
            0,
            int(
                self._safe_float(
                    source_counts.get(
                        "voice",
                        0
                    )
                )
            )
        )

        duration_component = (
            self._normalize(
                duration,
                self.duration_low,
                self.duration_high
            )
        )

        if voice_events > 0:

            voice_error_component = (
                self._normalize(
                    voice_error_rate,
                    self.voice_error_low,
                    self.voice_error_high
                )
            )

        else:

            voice_error_component = 0.0

        if (
            action_interval_samples
            > 0
        ):

            action_interval_component = (
                self._normalize(
                    action_interval,
                    self.action_interval_low,
                    self.action_interval_high
                )
            )

        else:

            action_interval_component = (
                0.0
            )

        if (
            movement_samples >= 2
            and average_movement > 0.0
        ):

            movement_ratio = (
                movement_variability
                / average_movement
            )

            movement_component = (
                self._normalize(
                    movement_ratio,
                    self.movement_variability_low,
                    self.movement_variability_high
                )
            )

        else:

            movement_component = 0.0

        duration_for_rate = max(
            duration,
            60.0
        )

        switches_per_minute = (
            user_switches
            * 60.0
            / duration_for_rate
        )

        switching_component = (
            self._normalize(
                switches_per_minute,
                self.switching_low,
                self.switching_high
            )
        )

        score = (
            duration_component
            * self.DURATION_WEIGHT

            + voice_error_component
            * self.VOICE_ERROR_WEIGHT

            + action_interval_component
            * self.ACTION_INTERVAL_WEIGHT

            + movement_component
            * self.MOVEMENT_WEIGHT

            + switching_component
            * self.SWITCHING_WEIGHT
        )

        score = self._clamp(
            score
        )

        return FatigueEstimate(
            score=round(
                score,
                4
            ),

            level=self._classify(
                score
            ),

            duration_component=round(
                duration_component,
                4
            ),

            voice_error_component=round(
                voice_error_component,
                4
            ),

            action_interval_component=round(
                action_interval_component,
                4
            ),

            movement_component=round(
                movement_component,
                4
            ),

            switching_component=round(
                switching_component,
                4
            ),
        )