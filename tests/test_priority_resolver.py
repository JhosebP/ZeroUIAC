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

from modules.multimodal.priority_resolver import (
    PriorityResolver
)


def test_voice_wins_over_gesture_on_action_conflict():

    resolver = PriorityResolver()

    voice_event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY,
        confidence=0.90
    )

    gesture_event = InteractionEvent(
        source=EventSource.GESTURE,
        event_type=EventType.ACTION,
        action=SystemAction.PASTE,
        confidence=0.99
    )

    result = resolver.resolve([
        gesture_event,
        voice_event
    ])

    assert len(result) == 1
    assert result[0] == voice_event


def test_cursor_and_action_can_coexist():

    resolver = PriorityResolver()

    head_event = InteractionEvent(
        source=EventSource.HEAD,
        event_type=EventType.CURSOR_MOVE,
        payload={
            "dx": 5,
            "dy": 2
        }
    )

    voice_event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY
    )

    result = resolver.resolve([
        head_event,
        voice_event
    ])

    assert len(result) == 2

    assert head_event in result
    assert voice_event in result


def test_manual_priority_can_override_source_priority():

    resolver = PriorityResolver()

    voice_event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY,
        priority=0
    )

    gesture_event = InteractionEvent(
        source=EventSource.GESTURE,
        event_type=EventType.ACTION,
        action=SystemAction.PASTE,
        priority=10
    )

    result = resolver.resolve([
        voice_event,
        gesture_event
    ])

    assert len(result) == 1
    assert result[0] == gesture_event


def test_empty_event_list():

    resolver = PriorityResolver()

    result = resolver.resolve([])

    assert result == []