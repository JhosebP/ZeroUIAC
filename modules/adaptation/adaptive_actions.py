from enum import Enum


class AdaptiveAction(str, Enum):
    """
    Acciones permitidas al agente
    adaptativo.

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

    INCREASE_VOICE_WEIGHT = (
        "increase_voice_weight"
    )

    DECREASE_VOICE_WEIGHT = (
        "decrease_voice_weight"
    )

    INCREASE_HEAD_WEIGHT = (
        "increase_head_weight"
    )

    DECREASE_HEAD_WEIGHT = (
        "decrease_head_weight"
    )

    INCREASE_LIMB_WEIGHT = (
        "increase_limb_weight"
    )

    DECREASE_LIMB_WEIGHT = (
        "decrease_limb_weight"
    )

    INCREASE_GESTURE_WEIGHT = (
        "increase_gesture_weight"
    )

    DECREASE_GESTURE_WEIGHT = (
        "decrease_gesture_weight"
    )