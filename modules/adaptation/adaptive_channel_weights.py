import threading
from dataclasses import dataclass

from domain.events.event_types import (
    EventSource,
)


@dataclass(frozen=True)
class ChannelWeightsSnapshot:
    """
    Copia inmutable de los pesos
    adaptativos de los canales.
    """

    voice: float
    head: float
    limb: float
    gesture: float

    def as_dict(self):

        return {
            "voice": self.voice,
            "head": self.head,
            "limb": self.limb,
            "gesture": self.gesture,
        }


class AdaptiveChannelWeights:
    """
    Gestiona los pesos adaptativos
    de los canales multimodales.

    Los pesos son factores relativos:

        1.0 = comportamiento neutral.

    Este componente no decide eventos,
    no ejecuta acciones y no conoce
    los controladores de Windows.
    """

    DEFAULT_WEIGHT = 1.0

    MIN_WEIGHT = 0.60
    MAX_WEIGHT = 1.40

    STEP = 0.05

    SUPPORTED_SOURCES = (
        EventSource.VOICE,
        EventSource.HEAD,
        EventSource.LIMB,
        EventSource.GESTURE,
    )

    def __init__(self):

        self._lock = (
            threading.RLock()
        )

        self._weights = {
            source: self.DEFAULT_WEIGHT
            for source
            in self.SUPPORTED_SOURCES
        }

    def _clamp(
        self,
        value,
    ):

        return max(
            self.MIN_WEIGHT,
            min(
                self.MAX_WEIGHT,
                round(
                    float(value),
                    2,
                ),
            ),
        )

    def _validate_adjustable_source(
        self,
        source,
    ):

        if (
            source
            not in self.SUPPORTED_SOURCES
        ):

            raise ValueError(
                "Canal adaptativo inválido."
            )

    def get_weight(
        self,
        source,
    ):
        """
        Obtiene el peso actual del canal.

        Los eventos SYSTEM mantienen
        siempre peso neutral.
        """

        if source == EventSource.SYSTEM:

            return self.DEFAULT_WEIGHT

        self._validate_adjustable_source(
            source
        )

        with self._lock:

            return self._weights[
                source
            ]

    def increase(
        self,
        source,
    ):
        """
        Incrementa gradualmente el peso
        de un canal.
        """

        self._validate_adjustable_source(
            source
        )

        with self._lock:

            previous = (
                self._weights[source]
            )

            self._weights[source] = (
                self._clamp(
                    previous
                    + self.STEP
                )
            )

            return (
                self._weights[source]
                != previous
            )

    def decrease(
        self,
        source,
    ):
        """
        Reduce gradualmente el peso
        de un canal.
        """

        self._validate_adjustable_source(
            source
        )

        with self._lock:

            previous = (
                self._weights[source]
            )

            self._weights[source] = (
                self._clamp(
                    previous
                    - self.STEP
                )
            )

            return (
                self._weights[source]
                != previous
            )

    def snapshot(self):

        with self._lock:

            return ChannelWeightsSnapshot(
                voice=self._weights[
                    EventSource.VOICE
                ],
                head=self._weights[
                    EventSource.HEAD
                ],
                limb=self._weights[
                    EventSource.LIMB
                ],
                gesture=self._weights[
                    EventSource.GESTURE
                ],
            )

    def reset(self):
        """
        Restaura todos los canales
        al peso neutral.
        """

        with self._lock:

            for source in (
                self.SUPPORTED_SOURCES
            ):

                self._weights[source] = (
                    self.DEFAULT_WEIGHT
                )