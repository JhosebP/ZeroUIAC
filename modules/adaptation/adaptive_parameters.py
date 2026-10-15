import threading
from dataclasses import dataclass

from modules.adaptation.adaptive_actions import (
    AdaptiveAction,
)


@dataclass(frozen=True)
class AdaptiveParametersSnapshot:
    """
    Copia inmutable de los parámetros
    adaptativos actuales.
    """

    head_sensitivity_factor: float
    limb_sensitivity_factor: float


class AdaptiveParametersManager:
    """
    Mantiene parámetros adaptativos dentro
    de límites estrictamente controlados.

    Los factores son multiplicadores
    normalizados:

        1.0 = comportamiento original.

    Este componente no conoce Windows,
    PyAutoGUI ni los controladores físicos.
    """

    DEFAULT_FACTOR = 1.0

    MIN_FACTOR = 0.60
    MAX_FACTOR = 1.40

    STEP = 0.05

    def __init__(self):

        self._lock = (
            threading.RLock()
        )

        self._head_factor = (
            self.DEFAULT_FACTOR
        )

        self._limb_factor = (
            self.DEFAULT_FACTOR
        )

    def _clamp(
        self,
        value,
    ):

        return max(
            self.MIN_FACTOR,
            min(
                self.MAX_FACTOR,
                round(
                    value,
                    2,
                ),
            ),
        )

    def apply(
        self,
        action,
    ):
        """
        Aplica una acción adaptativa.

        Retorna True únicamente cuando
        algún parámetro realmente cambió.
        """

        if not isinstance(
            action,
            AdaptiveAction,
        ):
            raise ValueError(
                "Acción adaptativa inválida."
            )

        with self._lock:

            previous_head = (
                self._head_factor
            )

            previous_limb = (
                self._limb_factor
            )

            if (
                action
                == AdaptiveAction.NO_CHANGE
            ):

                return False

            if (
                action
                == AdaptiveAction
                .INCREASE_HEAD_SENSITIVITY
            ):

                self._head_factor = (
                    self._clamp(
                        self._head_factor
                        + self.STEP
                    )
                )

            elif (
                action
                == AdaptiveAction
                .DECREASE_HEAD_SENSITIVITY
            ):

                self._head_factor = (
                    self._clamp(
                        self._head_factor
                        - self.STEP
                    )
                )

            elif (
                action
                == AdaptiveAction
                .INCREASE_LIMB_SENSITIVITY
            ):

                self._limb_factor = (
                    self._clamp(
                        self._limb_factor
                        + self.STEP
                    )
                )

            elif (
                action
                == AdaptiveAction
                .DECREASE_LIMB_SENSITIVITY
            ):

                self._limb_factor = (
                    self._clamp(
                        self._limb_factor
                        - self.STEP
                    )
                )

            return (
                previous_head
                != self._head_factor
                or previous_limb
                != self._limb_factor
            )

    def snapshot(self):

        with self._lock:

            return (
                AdaptiveParametersSnapshot(
                    head_sensitivity_factor=(
                        self._head_factor
                    ),
                    limb_sensitivity_factor=(
                        self._limb_factor
                    ),
                )
            )

    def reset(self):
        """
        Restaura los parámetros originales.
        """

        with self._lock:

            self._head_factor = (
                self.DEFAULT_FACTOR
            )

            self._limb_factor = (
                self.DEFAULT_FACTOR
            )