import pytest

from domain.events.event_types import (
    EventSource,
)

from modules.adaptation.adaptive_channel_weights import (
    AdaptiveChannelWeights,
)


def test_all_channel_weights_start_neutral():

    manager = (
        AdaptiveChannelWeights()
    )

    snapshot = manager.snapshot()

    assert snapshot.voice == 1.0
    assert snapshot.head == 1.0
    assert snapshot.limb == 1.0
    assert snapshot.gesture == 1.0


def test_voice_weight_can_increase():

    manager = (
        AdaptiveChannelWeights()
    )

    changed = manager.increase(
        EventSource.VOICE
    )

    assert changed is True

    assert (
        manager.get_weight(
            EventSource.VOICE
        )
        == 1.05
    )


def test_head_weight_can_decrease():

    manager = (
        AdaptiveChannelWeights()
    )

    changed = manager.decrease(
        EventSource.HEAD
    )

    assert changed is True

    assert (
        manager.get_weight(
            EventSource.HEAD
        )
        == 0.95
    )


def test_limb_change_does_not_modify_other_channels():

    manager = (
        AdaptiveChannelWeights()
    )

    manager.increase(
        EventSource.LIMB
    )

    snapshot = manager.snapshot()

    assert snapshot.limb == 1.05
    assert snapshot.voice == 1.0
    assert snapshot.head == 1.0
    assert snapshot.gesture == 1.0


def test_gesture_weight_can_decrease_independently():

    manager = (
        AdaptiveChannelWeights()
    )

    manager.decrease(
        EventSource.GESTURE
    )

    snapshot = manager.snapshot()

    assert snapshot.gesture == 0.95
    assert snapshot.voice == 1.0
    assert snapshot.head == 1.0
    assert snapshot.limb == 1.0


def test_weight_cannot_exceed_maximum():

    manager = (
        AdaptiveChannelWeights()
    )

    for _ in range(100):

        manager.increase(
            EventSource.VOICE
        )

    assert (
        manager.get_weight(
            EventSource.VOICE
        )
        == manager.MAX_WEIGHT
    )


def test_weight_cannot_go_below_minimum():

    manager = (
        AdaptiveChannelWeights()
    )

    for _ in range(100):

        manager.decrease(
            EventSource.HEAD
        )

    assert (
        manager.get_weight(
            EventSource.HEAD
        )
        == manager.MIN_WEIGHT
    )


def test_system_source_always_has_neutral_weight():

    manager = (
        AdaptiveChannelWeights()
    )

    assert (
        manager.get_weight(
            EventSource.SYSTEM
        )
        == 1.0
    )


def test_system_source_cannot_be_adjusted():

    manager = (
        AdaptiveChannelWeights()
    )

    with pytest.raises(
        ValueError
    ):

        manager.increase(
            EventSource.SYSTEM
        )


def test_reset_restores_all_weights():

    manager = (
        AdaptiveChannelWeights()
    )

    manager.increase(
        EventSource.VOICE
    )

    manager.decrease(
        EventSource.HEAD
    )

    manager.increase(
        EventSource.LIMB
    )

    manager.decrease(
        EventSource.GESTURE
    )

    manager.reset()

    snapshot = manager.snapshot()

    assert snapshot.voice == 1.0
    assert snapshot.head == 1.0
    assert snapshot.limb == 1.0
    assert snapshot.gesture == 1.0


def test_previous_snapshot_does_not_change():

    manager = (
        AdaptiveChannelWeights()
    )

    first_snapshot = (
        manager.snapshot()
    )

    manager.increase(
        EventSource.VOICE
    )

    second_snapshot = (
        manager.snapshot()
    )

    assert first_snapshot.voice == 1.0
    assert second_snapshot.voice == 1.05