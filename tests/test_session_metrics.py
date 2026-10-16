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

def test_operational_metrics_start_at_zero():

    metrics = SessionMetrics()

    snapshot = metrics.snapshot()

    assert snapshot[
        "voice_error_events"
    ] == 0

    assert snapshot[
        "user_channel_switches"
    ] == 0

    assert snapshot[
        "average_action_interval_seconds"
    ] == 0.0

    assert snapshot[
        "movement_variability"
    ] == 0.0

    assert snapshot[
        "movement_samples"
    ] == 0


def test_voice_error_is_recorded_separately():

    metrics = SessionMetrics()

    metrics.record_event(
        InteractionEvent(
            source=EventSource.VOICE,
            event_type=EventType.STATUS,
            payload={
                "level": "error"
            }
        )
    )

    snapshot = metrics.snapshot()

    assert snapshot[
        "error_events"
    ] == 1

    assert snapshot[
        "voice_error_events"
    ] == 1

    assert snapshot[
        "voice_error_rate"
    ] == 1.0


def test_non_voice_error_does_not_count_as_voice_error():

    metrics = SessionMetrics()

    metrics.record_event(
        InteractionEvent(
            source=EventSource.SYSTEM,
            event_type=EventType.STATUS,
            payload={
                "level": "error"
            }
        )
    )

    snapshot = metrics.snapshot()

    assert snapshot[
        "error_events"
    ] == 1

    assert snapshot[
        "voice_error_events"
    ] == 0


def test_user_channel_switch_ignores_system_events():

    metrics = SessionMetrics()

    metrics.record_event(
        InteractionEvent(
            source=EventSource.HEAD,
            event_type=EventType.CURSOR_MOVE
        )
    )

    metrics.record_event(
        InteractionEvent(
            source=EventSource.SYSTEM,
            event_type=EventType.STATUS
        )
    )

    metrics.record_event(
        InteractionEvent(
            source=EventSource.HEAD,
            event_type=EventType.CURSOR_MOVE
        )
    )

    snapshot = metrics.snapshot()

    assert snapshot[
        "channel_switches"
    ] == 2

    assert snapshot[
        "user_channel_switches"
    ] == 0


def test_average_action_interval_is_recorded():

    metrics = SessionMetrics()

    metrics.record_event(
        InteractionEvent(
            source=EventSource.VOICE,
            event_type=EventType.ACTION,
            action=SystemAction.COPY,
            timestamp=10.0
        )
    )

    metrics.record_event(
        InteractionEvent(
            source=EventSource.VOICE,
            event_type=EventType.ACTION,
            action=SystemAction.PASTE,
            timestamp=13.0
        )
    )

    metrics.record_event(
        InteractionEvent(
            source=EventSource.VOICE,
            event_type=EventType.ACTION,
            action=SystemAction.COPY,
            timestamp=19.0
        )
    )

    snapshot = metrics.snapshot()

    assert snapshot[
        "action_interval_samples"
    ] == 2

    assert snapshot[
        "average_action_interval_seconds"
    ] == 4.5


def test_relative_movement_variability_is_recorded():

    metrics = SessionMetrics()

    metrics.record_event(
        InteractionEvent(
            source=EventSource.HEAD,
            event_type=EventType.CURSOR_MOVE,
            payload={
                "mode": "relative",
                "dx": 3,
                "dy": 4
            }
        )
    )

    metrics.record_event(
        InteractionEvent(
            source=EventSource.HEAD,
            event_type=EventType.CURSOR_MOVE,
            payload={
                "mode": "relative",
                "dx": 6,
                "dy": 8
            }
        )
    )

    snapshot = metrics.snapshot()

    assert snapshot[
        "movement_samples"
    ] == 2

    assert snapshot[
        "average_movement_magnitude"
    ] == 7.5

    assert snapshot[
        "movement_variability"
    ] == 2.5


def test_absolute_movement_variability_is_recorded():

    metrics = SessionMetrics()

    positions = (
        (100, 100),
        (103, 104),
        (109, 112),
    )

    for x, y in positions:

        metrics.record_event(
            InteractionEvent(
                source=EventSource.LIMB,
                event_type=EventType.CURSOR_MOVE,
                payload={
                    "mode": "absolute",
                    "x": x,
                    "y": y
                }
            )
        )

    snapshot = metrics.snapshot()

    assert snapshot[
        "movement_samples"
    ] == 2

    assert snapshot[
        "average_movement_magnitude"
    ] == 7.5

    assert snapshot[
        "movement_variability"
    ] == 2.5