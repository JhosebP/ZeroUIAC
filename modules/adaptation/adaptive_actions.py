from enum import Enum


class AdaptiveAction(str, Enum):
    """
    Acciones permitidas al futuro
    agente adaptativo.

    Ninguna acción interactúa
    directamente con Windows.
    """

    NO_CHANGE = "no_change"

    INCREASE_HEAD_SENSITIVITY = (
        "increase_head_sensitivity"
    )

    DECREASE_HEAD_SENSITIVITY = (
        "decrease_head_sensitivity"
    )

    INCREASE_LIMB_SENSITIVITY = (
        "increase_limb_sensitivity"
    )

    DECREASE_LIMB_SENSITIVITY = (
        "decrease_limb_sensitivity"
    )