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

from modules.adaptation.session_manager import (
    SessionManager
)


def test_session_is_inactive_by_default():

    manager = SessionManager()

    assert (
        manager.is_active
        is False
    )

    assert (
        manager.session_id
        is None
    )


def test_start_session():

    manager = SessionManager()

    session_id = (
        manager.start_session()
    )

    assert (
        manager.is_active
        is True
    )

    assert (
        session_id
        is not None
    )

    assert (
        manager.session_id
        == session_id
    )


def test_start_session_twice_keeps_same_session():

    manager = SessionManager()

    first_id = (
        manager.start_session()
    )

    second_id = (
        manager.start_session()
    )

    assert (
        first_id
        == second_id
    )


def test_event_is_ignored_without_active_session():

    manager = SessionManager()

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY
    )

    result = (
        manager.record_event(
            event
        )
    )

    assert result is False


def test_event_is_recorded_during_session():

    manager = SessionManager()

    manager.start_session()

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY
    )

    result = (
        manager.record_event(
            event
        )
    )

    snapshot = (
        manager.get_snapshot()
    )

    assert result is True

    assert (
        snapshot["metrics"]
        ["total_events"]
        == 1
    )

    assert (
        snapshot["metrics"]
        ["action_events"]
        == 1
    )


def test_end_session_returns_summary():

    manager = SessionManager()

    session_id = (
        manager.start_session()
    )

    manager.record_event(
        InteractionEvent(
            source=EventSource.HEAD,
            event_type=(
                EventType.CURSOR_MOVE
            )
        )
    )

    summary = (
        manager.end_session()
    )

    assert (
        summary["session_id"]
        == session_id
    )

    assert (
        summary["metrics"]
        ["total_events"]
        == 1
    )

    assert (
        summary["started_at"]
        is not None
    )

    assert (
        summary["ended_at"]
        is not None
    )

    assert (
        manager.is_active
        is False
    )


def test_snapshot_is_none_without_active_session():

    manager = SessionManager()

    assert (
        manager.get_snapshot()
        is None
    )


def test_last_summary_is_preserved():

    manager = SessionManager()

    manager.start_session()

    summary = (
        manager.end_session()
    )

    assert (
        manager.get_last_summary()
        == summary
    )