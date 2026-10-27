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

from modules.adaptation.interaction_outcome_tracker import (
    InteractionOutcomeTracker
)


def relative_event(
    dx,
    dy
):

    return InteractionEvent(
        source=EventSource.HEAD,
        event_type=EventType.CURSOR_MOVE,
        payload={
            "mode": "relative",
            "dx": dx,
            "dy": dy,
        }
    )


def absolute_event(
    x,
    y
):

    return InteractionEvent(
        source=EventSource.LIMB,
        event_type=EventType.CURSOR_MOVE,
        payload={
            "mode": "absolute",
            "x": x,
            "y": y,
        }
    )


def test_tracker_starts_empty():

    tracker = (
        InteractionOutcomeTracker()
    )

    snapshot = tracker.snapshot()

    assert (
        snapshot["action_attempts"]
        == 0
    )

    assert (
        snapshot["drag_successes"]
        == 0
    )

    assert (
        snapshot["correction_rate"]
        == 0.0
    )


def test_successful_action_is_recorded():

    tracker = (
        InteractionOutcomeTracker()
    )

    tracker.record_action_result(
        SystemAction.COPY,
        True
    )

    snapshot = tracker.snapshot()

    assert (
        snapshot["action_attempts"]
        == 1
    )

    assert (
        snapshot["action_successes"]
        == 1
    )

    assert (
        snapshot["action_failures"]
        == 0
    )


def test_failed_action_is_recorded():

    tracker = (
        InteractionOutcomeTracker()
    )

    tracker.record_action_result(
        SystemAction.START_DRAG,
        False
    )

    snapshot = tracker.snapshot()

    assert (
        snapshot["action_failures"]
        == 1
    )

    assert (
        snapshot["drag_failures"]
        == 1
    )


def test_successful_drag_requires_movement():

    tracker = (
        InteractionOutcomeTracker()
    )

    tracker.record_action_result(
        SystemAction.START_DRAG,
        True
    )

    tracker.record_cursor_event(
        relative_event(
            10,
            0
        )
    )

    tracker.record_action_result(
        SystemAction.STOP_DRAG,
        True
    )

    snapshot = tracker.snapshot()

    assert (
        snapshot["drag_successes"]
        == 1
    )

    assert (
        snapshot["drag_failures"]
        == 0
    )


def test_drag_without_movement_is_failure():

    tracker = (
        InteractionOutcomeTracker()
    )

    tracker.record_action_result(
        SystemAction.START_DRAG,
        True
    )

    tracker.record_action_result(
        SystemAction.STOP_DRAG,
        True
    )

    snapshot = tracker.snapshot()

    assert (
        snapshot["drag_successes"]
        == 0
    )

    assert (
        snapshot["drag_failures"]
        == 1
    )


def test_click_interrupts_drag():

    tracker = (
        InteractionOutcomeTracker()
    )

    tracker.record_action_result(
        SystemAction.START_DRAG,
        True
    )

    tracker.record_cursor_event(
        relative_event(
            10,
            0
        )
    )

    tracker.record_action_result(
        SystemAction.LEFT_CLICK,
        True
    )

    snapshot = tracker.snapshot()

    assert (
        snapshot["drag_failures"]
        == 1
    )

    assert (
        snapshot["drag_active"]
        is False
    )


def test_relative_direction_reversal_counts_correction():

    tracker = (
        InteractionOutcomeTracker()
    )

    tracker.record_cursor_event(
        relative_event(
            10,
            0
        )
    )

    tracker.record_cursor_event(
        relative_event(
            -10,
            0
        )
    )

    snapshot = tracker.snapshot()

    assert (
        snapshot["cursor_samples"]
        == 2
    )

    assert (
        snapshot["correction_events"]
        == 1
    )

    assert (
        snapshot["correction_rate"]
        == 0.5
    )


def test_same_direction_does_not_count_correction():

    tracker = (
        InteractionOutcomeTracker()
    )

    tracker.record_cursor_event(
        relative_event(
            10,
            0
        )
    )

    tracker.record_cursor_event(
        relative_event(
            5,
            1
        )
    )

    snapshot = tracker.snapshot()

    assert (
        snapshot["correction_events"]
        == 0
    )


def test_absolute_direction_reversal_counts_correction():

    tracker = (
        InteractionOutcomeTracker()
    )

    tracker.record_cursor_event(
        absolute_event(
            100,
            100
        )
    )

    tracker.record_cursor_event(
        absolute_event(
            120,
            100
        )
    )

    tracker.record_cursor_event(
        absolute_event(
            105,
            100
        )
    )

    snapshot = tracker.snapshot()

    assert (
        snapshot["cursor_samples"]
        == 2
    )

    assert (
        snapshot["correction_events"]
        == 1
    )


def test_pending_drag_is_failure_on_finalize():

    tracker = (
        InteractionOutcomeTracker()
    )

    tracker.record_action_result(
        SystemAction.START_DRAG,
        True
    )

    tracker.record_cursor_event(
        relative_event(
            5,
            0
        )
    )

    result = (
        tracker.finalize_pending_drag()
    )

    assert result is True

    snapshot = tracker.snapshot()

    assert (
        snapshot["drag_failures"]
        == 1
    )

    assert (
        snapshot["drag_active"]
        is False
    )