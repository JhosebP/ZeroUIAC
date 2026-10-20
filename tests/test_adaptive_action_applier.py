import pytest

from domain.events.event_types import (
    EventSource
)

from modules.adaptation.adaptive_actions import (
    AdaptiveAction
)

from modules.adaptation.adaptive_parameters import (
    AdaptiveParametersManager
)

from modules.adaptation.adaptive_channel_weights import (
    AdaptiveChannelWeights
)

from modules.adaptation.adaptive_action_applier import (
    AdaptiveActionApplier
)


def create_applier():

    parameters = (
        AdaptiveParametersManager()
    )

    weights = (
        AdaptiveChannelWeights()
    )

    applier = (
        AdaptiveActionApplier(
            parameters_manager=parameters,
            channel_weights=weights,
        )
    )

    return (
        applier,
        parameters,
        weights
    )


def test_no_change_keeps_everything():

    (
        applier,
        parameters,
        weights
    ) = create_applier()

    changed = applier.apply(
        AdaptiveAction.NO_CHANGE
    )

    assert changed is False

    assert (
        parameters.snapshot()
        .head_sensitivity_factor
        == 1.0
    )

    assert (
        weights.get_weight(
            EventSource.VOICE
        )
        == 1.0
    )


def test_increase_head_sensitivity():

    (
        applier,
        parameters,
        _
    ) = create_applier()

    changed = applier.apply(
        AdaptiveAction
        .INCREASE_HEAD_SENSITIVITY
    )

    assert changed is True

    assert (
        parameters.snapshot()
        .head_sensitivity_factor
        == 1.05
    )


def test_decrease_limb_sensitivity():

    (
        applier,
        parameters,
        _
    ) = create_applier()

    applier.apply(
        AdaptiveAction
        .DECREASE_LIMB_SENSITIVITY
    )

    assert (
        parameters.snapshot()
        .limb_sensitivity_factor
        == 0.95
    )


def test_increase_voice_weight():

    (
        applier,
        _,
        weights
    ) = create_applier()

    applier.apply(
        AdaptiveAction
        .INCREASE_VOICE_WEIGHT
    )

    assert (
        weights.get_weight(
            EventSource.VOICE
        )
        == 1.05
    )


def test_decrease_gesture_weight():

    (
        applier,
        _,
        weights
    ) = create_applier()

    applier.apply(
        AdaptiveAction
        .DECREASE_GESTURE_WEIGHT
    )

    assert (
        weights.get_weight(
            EventSource.GESTURE
        )
        == 0.95
    )


def test_channel_weight_action_does_not_change_sensitivity():

    (
        applier,
        parameters,
        _
    ) = create_applier()

    applier.apply(
        AdaptiveAction
        .INCREASE_HEAD_WEIGHT
    )

    snapshot = (
        parameters.snapshot()
    )

    assert (
        snapshot.head_sensitivity_factor
        == 1.0
    )

    assert (
        snapshot.limb_sensitivity_factor
        == 1.0
    )


def test_invalid_action_is_rejected():

    (
        applier,
        _,
        _
    ) = create_applier()

    with pytest.raises(
        ValueError
    ):

        applier.apply(
            "invalid"
        )