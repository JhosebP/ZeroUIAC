import pytest

from modules.adaptation.adaptive_actions import (
    AdaptiveAction,
)

from modules.adaptation.adaptive_parameters import (
    AdaptiveParametersManager,
)


def test_default_parameters_are_neutral():

    manager = (
        AdaptiveParametersManager()
    )

    snapshot = (
        manager.snapshot()
    )

    assert (
        snapshot.head_sensitivity_factor
        == 1.0
    )

    assert (
        snapshot.limb_sensitivity_factor
        == 1.0
    )


def test_increase_head_sensitivity():

    manager = (
        AdaptiveParametersManager()
    )

    changed = manager.apply(
        AdaptiveAction
        .INCREASE_HEAD_SENSITIVITY
    )

    snapshot = (
        manager.snapshot()
    )

    assert changed is True

    assert (
        snapshot.head_sensitivity_factor
        == 1.05
    )

    assert (
        snapshot.limb_sensitivity_factor
        == 1.0
    )


def test_decrease_head_sensitivity():

    manager = (
        AdaptiveParametersManager()
    )

    manager.apply(
        AdaptiveAction
        .DECREASE_HEAD_SENSITIVITY
    )

    assert (
        manager.snapshot()
        .head_sensitivity_factor
        == 0.95
    )


def test_increase_limb_sensitivity():

    manager = (
        AdaptiveParametersManager()
    )

    manager.apply(
        AdaptiveAction
        .INCREASE_LIMB_SENSITIVITY
    )

    snapshot = (
        manager.snapshot()
    )

    assert (
        snapshot.limb_sensitivity_factor
        == 1.05
    )

    assert (
        snapshot.head_sensitivity_factor
        == 1.0
    )


def test_decrease_limb_sensitivity():

    manager = (
        AdaptiveParametersManager()
    )

    manager.apply(
        AdaptiveAction
        .DECREASE_LIMB_SENSITIVITY
    )

    assert (
        manager.snapshot()
        .limb_sensitivity_factor
        == 0.95
    )


def test_no_change_keeps_parameters():

    manager = (
        AdaptiveParametersManager()
    )

    changed = manager.apply(
        AdaptiveAction.NO_CHANGE
    )

    snapshot = (
        manager.snapshot()
    )

    assert changed is False

    assert (
        snapshot.head_sensitivity_factor
        == 1.0
    )

    assert (
        snapshot.limb_sensitivity_factor
        == 1.0
    )


def test_head_factor_cannot_exceed_maximum():

    manager = (
        AdaptiveParametersManager()
    )

    for _ in range(100):

        manager.apply(
            AdaptiveAction
            .INCREASE_HEAD_SENSITIVITY
        )

    assert (
        manager.snapshot()
        .head_sensitivity_factor
        == manager.MAX_FACTOR
    )


def test_head_factor_cannot_go_below_minimum():

    manager = (
        AdaptiveParametersManager()
    )

    for _ in range(100):

        manager.apply(
            AdaptiveAction
            .DECREASE_HEAD_SENSITIVITY
        )

    assert (
        manager.snapshot()
        .head_sensitivity_factor
        == manager.MIN_FACTOR
    )


def test_limb_factor_cannot_exceed_maximum():

    manager = (
        AdaptiveParametersManager()
    )

    for _ in range(100):

        manager.apply(
            AdaptiveAction
            .INCREASE_LIMB_SENSITIVITY
        )

    assert (
        manager.snapshot()
        .limb_sensitivity_factor
        == manager.MAX_FACTOR
    )


def test_limb_factor_cannot_go_below_minimum():

    manager = (
        AdaptiveParametersManager()
    )

    for _ in range(100):

        manager.apply(
            AdaptiveAction
            .DECREASE_LIMB_SENSITIVITY
        )

    assert (
        manager.snapshot()
        .limb_sensitivity_factor
        == manager.MIN_FACTOR
    )


def test_reset_restores_default_values():

    manager = (
        AdaptiveParametersManager()
    )

    manager.apply(
        AdaptiveAction
        .INCREASE_HEAD_SENSITIVITY
    )

    manager.apply(
        AdaptiveAction
        .DECREASE_LIMB_SENSITIVITY
    )

    manager.reset()

    snapshot = (
        manager.snapshot()
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

    manager = (
        AdaptiveParametersManager()
    )

    with pytest.raises(
        ValueError
    ):

        manager.apply(
            "accion_inventada"
        )