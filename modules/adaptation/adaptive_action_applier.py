from domain.events.event_types import (
    EventSource
)

from modules.adaptation.adaptive_actions import (
    AdaptiveAction
)


class AdaptiveActionApplier:
    """
    Aplica únicamente cambios acotados
    sobre parámetros adaptativos.

    No conoce controladores de Windows.
    """

    SENSITIVITY_ACTIONS = {
        AdaptiveAction
        .INCREASE_HEAD_SENSITIVITY,

        AdaptiveAction
        .DECREASE_HEAD_SENSITIVITY,

        AdaptiveAction
        .INCREASE_LIMB_SENSITIVITY,

        AdaptiveAction
        .DECREASE_LIMB_SENSITIVITY,
    }

    CHANNEL_ACTIONS = {

        AdaptiveAction
        .INCREASE_VOICE_WEIGHT:
            (
                EventSource.VOICE,
                "increase"
            ),

        AdaptiveAction
        .DECREASE_VOICE_WEIGHT:
            (
                EventSource.VOICE,
                "decrease"
            ),

        AdaptiveAction
        .INCREASE_HEAD_WEIGHT:
            (
                EventSource.HEAD,
                "increase"
            ),

        AdaptiveAction
        .DECREASE_HEAD_WEIGHT:
            (
                EventSource.HEAD,
                "decrease"
            ),

        AdaptiveAction
        .INCREASE_LIMB_WEIGHT:
            (
                EventSource.LIMB,
                "increase"
            ),

        AdaptiveAction
        .DECREASE_LIMB_WEIGHT:
            (
                EventSource.LIMB,
                "decrease"
            ),

        AdaptiveAction
        .INCREASE_GESTURE_WEIGHT:
            (
                EventSource.GESTURE,
                "increase"
            ),

        AdaptiveAction
        .DECREASE_GESTURE_WEIGHT:
            (
                EventSource.GESTURE,
                "decrease"
            ),
    }

    def __init__(
        self,
        parameters_manager=None,
        channel_weights=None
    ):

        self.parameters_manager = (
            parameters_manager
        )

        self.channel_weights = (
            channel_weights
        )

    def apply(
        self,
        action
    ):
        """
        Aplica como máximo un cambio
        adaptativo por llamada.
        """

        if not isinstance(
            action,
            AdaptiveAction
        ):

            raise ValueError(
                "Acción adaptativa inválida."
            )

        if (
            action
            == AdaptiveAction.NO_CHANGE
        ):

            return False

        if (
            action
            in self.SENSITIVITY_ACTIONS
        ):

            if (
                self.parameters_manager
                is None
            ):

                return False

            return (
                self.parameters_manager
                .apply(
                    action
                )
            )

        configuration = (
            self.CHANNEL_ACTIONS.get(
                action
            )
        )

        if configuration is None:

            raise ValueError(
                "Acción adaptativa no soportada."
            )

        if self.channel_weights is None:

            return False

        source, operation = (
            configuration
        )

        if operation == "increase":

            return (
                self.channel_weights
                .increase(
                    source
                )
            )

        return (
            self.channel_weights
            .decrease(
                source
            )
        )