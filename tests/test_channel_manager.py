from domain.events.event_types import (
    EventSource
)

from modules.multimodal.channel_manager import (
    ChannelManager
)


def test_channels_enabled_by_default():

    manager = ChannelManager()

    assert manager.is_enabled(
        EventSource.VOICE
    )

    assert manager.is_enabled(
        EventSource.HEAD
    )

    assert manager.is_enabled(
        EventSource.LIMB
    )

    assert manager.is_enabled(
        EventSource.GESTURE
    )


def test_disable_channel():

    manager = ChannelManager()

    manager.disable(
        EventSource.HEAD
    )

    assert (
        manager.is_enabled(
            EventSource.HEAD
        )
        is False
    )


def test_enable_channel():

    manager = ChannelManager()

    manager.disable(
        EventSource.VOICE
    )

    manager.enable(
        EventSource.VOICE
    )

    assert manager.is_enabled(
        EventSource.VOICE
    )


def test_set_enabled():

    manager = ChannelManager()

    manager.set_enabled(
        EventSource.LIMB,
        False
    )

    assert (
        manager.is_enabled(
            EventSource.LIMB
        )
        is False
    )


def test_get_enabled_sources():

    manager = ChannelManager()

    manager.disable(
        EventSource.HEAD
    )

    enabled = (
        manager.get_enabled_sources()
    )

    assert EventSource.HEAD not in enabled

    assert EventSource.VOICE in enabled
    assert EventSource.LIMB in enabled