from domain.commands.system_actions import (
    SystemAction
)

from domain.events.event_types import (
    EventSource,
    EventType
)

from domain.events.interaction_event import (
    InteractionEvent
)

from modules.multimodal.channel_manager import (
    ChannelManager
)

from modules.multimodal.fusion_engine import (
    FusionEngine
)


def test_single_event_passes():

    engine = FusionEngine()

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY
    )

    result = engine.process_event(
        event
    )

    assert len(result) == 1
    assert result[0] == event


def test_voice_and_head_can_work_together():

    engine = FusionEngine()

    voice_event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY
    )

    head_event = InteractionEvent(
        source=EventSource.HEAD,
        event_type=EventType.CURSOR_MOVE,
        payload={
            "dx": 4,
            "dy": -2
        }
    )

    result = engine.process_events([
        voice_event,
        head_event
    ])

    assert len(result) == 2

    assert voice_event in result
    assert head_event in result


def test_disabled_channel_is_ignored():

    manager = ChannelManager()

    manager.disable(
        EventSource.VOICE
    )

    engine = FusionEngine(
        channel_manager=manager
    )

    voice_event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY
    )

    result = engine.process_events([
        voice_event
    ])

    assert result == []


def test_voice_wins_conflicting_action():

    engine = FusionEngine()

    voice_event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY
    )

    gesture_event = InteractionEvent(
        source=EventSource.GESTURE,
        event_type=EventType.ACTION,
        action=SystemAction.PASTE
    )

    result = engine.process_events([
        gesture_event,
        voice_event
    ])

    assert len(result) == 1
    assert result[0] == voice_event


def test_empty_events():

    engine = FusionEngine()

    result = engine.process_events([])

    assert result == []