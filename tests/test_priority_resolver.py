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

from modules.adaptation.adaptive_channel_weights import (
    AdaptiveChannelWeights
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

def test_neutral_weights_preserve_original_priority():

    weights = (
        AdaptiveChannelWeights()
    )

    resolver = (
        PriorityResolver(
            channel_weights=weights
        )
    )

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

    result = resolver.resolve([
        gesture_event,
        voice_event
    ])

    assert result[0] == voice_event


def test_adaptive_weights_can_change_action_winner():

    weights = (
        AdaptiveChannelWeights()
    )

    for _ in range(100):

        weights.decrease(
            EventSource.VOICE
        )

        weights.increase(
            EventSource.GESTURE
        )

    resolver = (
        PriorityResolver(
            channel_weights=weights
        )
    )

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

    result = resolver.resolve([
        voice_event,
        gesture_event
    ])

    assert result[0] == gesture_event


def test_adaptive_weights_can_change_cursor_winner():

    weights = (
        AdaptiveChannelWeights()
    )

    for _ in range(100):

        weights.increase(
            EventSource.HEAD
        )

        weights.decrease(
            EventSource.LIMB
        )

    resolver = (
        PriorityResolver(
            channel_weights=weights
        )
    )

    head_event = InteractionEvent(
        source=EventSource.HEAD,
        event_type=EventType.CURSOR_MOVE,
        payload={
            "dx": 4,
            "dy": 2
        },
        conflict_key="cursor"
    )

    limb_event = InteractionEvent(
        source=EventSource.LIMB,
        event_type=EventType.CURSOR_MOVE,
        payload={
            "x": 500,
            "y": 300
        },
        conflict_key="cursor"
    )

    result = resolver.resolve([
        limb_event,
        head_event
    ])

    assert len(result) == 1

    assert result[0] == head_event


def test_manual_priority_still_overrides_adaptive_weight():

    weights = (
        AdaptiveChannelWeights()
    )

    for _ in range(100):

        weights.increase(
            EventSource.GESTURE
        )

        weights.decrease(
            EventSource.VOICE
        )

    resolver = (
        PriorityResolver(
            channel_weights=weights
        )
    )

    voice_event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY,
        priority=10
    )

    gesture_event = InteractionEvent(
        source=EventSource.GESTURE,
        event_type=EventType.ACTION,
        action=SystemAction.PASTE,
        priority=0
    )

    result = resolver.resolve([
        gesture_event,
        voice_event
    ])

    assert result[0] == voice_event


def test_system_always_beats_adaptive_user_channel():

    weights = (
        AdaptiveChannelWeights()
    )

    for _ in range(100):

        weights.increase(
            EventSource.VOICE
        )

    resolver = (
        PriorityResolver(
            channel_weights=weights
        )
    )

    system_event = InteractionEvent(
        source=EventSource.SYSTEM,
        event_type=EventType.ACTION,
        action=SystemAction.COPY,
        conflict_key="action"
    )

    voice_event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.PASTE,
        conflict_key="action"
    )

    result = resolver.resolve([
        voice_event,
        system_event
    ])

    assert result[0] == system_event