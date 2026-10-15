from domain.events.event_types import (
    EventSource,
    EventType
)

from domain.events.interaction_event import (
    InteractionEvent
)

from domain.commands.system_actions import (
    SystemAction
)

from modules.adaptation.session_metrics import (
    SessionMetrics
)


def test_metrics_start_empty():

    metrics = SessionMetrics()

    snapshot = (
        metrics.snapshot()
    )

    assert (
        snapshot["total_events"]
        == 0
    )

    assert (
        snapshot["error_events"]
        == 0
    )

    assert (
        snapshot["channel_switches"]
        == 0
    )


def test_action_event_is_recorded():

    metrics = SessionMetrics()

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY
    )

    metrics.record_event(
        event
    )

    snapshot = (
        metrics.snapshot()
    )

    assert (
        snapshot["total_events"]
        == 1
    )

    assert (
        snapshot["action_events"]
        == 1
    )

    assert (
        snapshot["source_counts"]["voice"]
        == 1
    )

def test_cursor_event_is_recorded():

    metrics = SessionMetrics()

    event = InteractionEvent(
        source=EventSource.HEAD,
        event_type=(
            EventType.CURSOR_MOVE
        )
    )

    metrics.record_event(
        event
    )

    snapshot = (
        metrics.snapshot()
    )

    assert (
        snapshot["cursor_events"]
        == 1
    )


def test_error_status_is_recorded():

    metrics = SessionMetrics()

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.STATUS,
        payload={
            "level": "error"
        }
    )

    metrics.record_event(
        event
    )

    snapshot = (
        metrics.snapshot()
    )

    assert (
        snapshot["error_events"]
        == 1
    )

    assert (
        snapshot["error_rate"]
        == 1.0
    )


def test_channel_switch_is_recorded():

    metrics = SessionMetrics()

    metrics.record_event(
        InteractionEvent(
            source=EventSource.HEAD,
            event_type=(
                EventType.CURSOR_MOVE
            )
        )
    )

    metrics.record_event(
        InteractionEvent(
            source=EventSource.LIMB,
            event_type=(
                EventType.CURSOR_MOVE
            )
        )
    )

    snapshot = (
        metrics.snapshot()
    )

    assert (
        snapshot["channel_switches"]
        == 1
    )


def test_same_channel_does_not_count_switch():

    metrics = SessionMetrics()

    for _ in range(3):

        metrics.record_event(
            InteractionEvent(
                source=EventSource.HEAD,
                event_type=(
                    EventType.CURSOR_MOVE
                )
            )
        )

    snapshot = (
        metrics.snapshot()
    )

    assert (
        snapshot["channel_switches"]
        == 0
    )