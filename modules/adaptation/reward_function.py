from dataclasses import dataclass


@dataclass(frozen=True)
class RewardContext:
    """
    Señales utilizadas para calcular
    la recompensa adaptativa.

    Todos los valores representan
    información del resultado de una
    interacción, no acciones de Windows.
    """

    success: bool = False
    error: bool = False

    latency_seconds: float = 0.0

    switch_rate: float = 0.0

    fatigue_level: float = 0.0


class RewardCalculator:
    """
    Calcula una recompensa escalar para
    el futuro agente Q-learning.

    No ejecuta acciones ni modifica
    parámetros del sistema.
    """

    SUCCESS_REWARD = 1.0

    ERROR_PENALTY = 2.0

    LATENCY_THRESHOLD = 1.5
    MAX_LATENCY_PENALTY = 0.50

    SWITCH_FREE_RATE = 2.0
    MAX_SWITCH_PENALTY = 0.50

    MAX_FATIGUE_PENALTY = 1.0

    MIN_REWARD = -4.0
    MAX_REWARD = 2.0

    def _clamp(
        self,
        value,
        minimum,
        maximum,
    ):

        return max(
            minimum,
            min(
                maximum,
                value,
            ),
        )

    def _latency_penalty(
        self,
        latency_seconds,
    ):

        latency = max(
            0.0,
            float(latency_seconds),
        )

        if (
            latency
            <= self.LATENCY_THRESHOLD
        ):
            return 0.0

        excess = (
            latency
            - self.LATENCY_THRESHOLD
        )

        penalty = (
            excess
            / self.LATENCY_THRESHOLD
            * self.MAX_LATENCY_PENALTY
        )

        return self._clamp(
            penalty,
            0.0,
            self.MAX_LATENCY_PENALTY,
        )

    def _switch_penalty(
        self,
        switch_rate,
    ):

        rate = max(
            0.0,
            float(switch_rate),
        )

        if (
            rate
            <= self.SWITCH_FREE_RATE
        ):
            return 0.0

        excess = (
            rate
            - self.SWITCH_FREE_RATE
        )

        penalty = (
            excess
            / self.SWITCH_FREE_RATE
            * self.MAX_SWITCH_PENALTY
        )

        return self._clamp(
            penalty,
            0.0,
            self.MAX_SWITCH_PENALTY,
        )

    def _fatigue_penalty(
        self,
        fatigue_level,
    ):

        fatigue = self._clamp(
            float(fatigue_level),
            0.0,
            1.0,
        )

        return (
            fatigue
            * self.MAX_FATIGUE_PENALTY
        )

    def calculate(
        self,
        context,
    ):
        """
        Calcula la recompensa final.

        Fatiga se expresa entre:

            0.0 = sin fatiga estimada
            1.0 = fatiga máxima estimada
        """

        if not isinstance(
            context,
            RewardContext,
        ):
            raise ValueError(
                "Contexto de recompensa inválido."
            )

        reward = 0.0

        if context.success:
            reward += (
                self.SUCCESS_REWARD
            )

        if context.error:
            reward -= (
                self.ERROR_PENALTY
            )

        reward -= (
            self._latency_penalty(
                context.latency_seconds
            )
        )

        reward -= (
            self._switch_penalty(
                context.switch_rate
            )
        )

        reward -= (
            self._fatigue_penalty(
                context.fatigue_level
            )
        )

        reward = self._clamp(
            reward,
            self.MIN_REWARD,
            self.MAX_REWARD,
        )

        return round(
            reward,
            3,
        )