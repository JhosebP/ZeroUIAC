from unittest.mock import MagicMock

from application.interaction.multimodal_coordinator import (
    MultimodalCoordinator
)

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


def create_coordinator(
    session_manager=None,
    interaction_outcome_tracker=None
):

    event_bus = MagicMock()
    fusion_engine = MagicMock()
    action_executor = MagicMock()
    mouse = MagicMock()

    coordinator = MultimodalCoordinator(
        event_bus=event_bus,
        fusion_engine=fusion_engine,
        action_executor=action_executor,
        mouse_controller=mouse,

        session_manager=(
            session_manager
        ),

        interaction_outcome_tracker=(
            interaction_outcome_tracker
        )
    )

    return (
        coordinator,
        event_bus,
        fusion_engine,
        action_executor,
        mouse
    )

def test_normal_action_records_outcome():

    tracker = MagicMock()

    (
        coordinator,
        _,
        _,
        action_executor,
        _
    ) = create_coordinator(
        interaction_outcome_tracker=tracker
    )

    action_executor.execute \
        .return_value = True

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY
    )

    coordinator._execute_event(
        event
    )

    tracker.record_action_result \
        .assert_called_once_with(
            SystemAction.COPY,
            True
        )


def test_failed_action_records_failure():

    tracker = MagicMock()

    (
        coordinator,
        _,
        _,
        action_executor,
        _
    ) = create_coordinator(
        interaction_outcome_tracker=tracker
    )

    action_executor.execute \
        .return_value = False

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.START_DRAG
    )

    coordinator._execute_event(
        event
    )

    tracker.record_action_result \
        .assert_called_once_with(
            SystemAction.START_DRAG,
            False
        )


def test_cursor_event_is_recorded_in_outcome_tracker():

    tracker = MagicMock()

    (
        coordinator,
        _,
        _,
        _,
        mouse
    ) = create_coordinator(
        interaction_outcome_tracker=tracker
    )

    mouse.move_relative \
        .return_value = True

    event = InteractionEvent(
        source=EventSource.HEAD,
        event_type=EventType.CURSOR_MOVE,
        payload={
            "mode": "relative",
            "dx": 5,
            "dy": 2
        }
    )

    coordinator._execute_event(
        event
    )

    tracker.record_cursor_event \
        .assert_called_once_with(
            event
        )


def test_stop_finalizes_pending_drag_outcome():

    tracker = MagicMock()

    (
        coordinator,
        _,
        _,
        _,
        _
    ) = create_coordinator(
        interaction_outcome_tracker=tracker
    )

    coordinator.stop()

    tracker.finalize_pending_drag \
        .assert_called_once()

def test_subscribes_to_event_bus():

    (
        coordinator,
        event_bus,
        _,
        _,
        _
    ) = create_coordinator()

    event_bus.subscribe_all \
        .assert_called_once_with(
            coordinator._receive_event
        )


def test_execute_action_event():

    (
        coordinator,
        _,
        _,
        action_executor,
        _
    ) = create_coordinator()

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY
    )

    coordinator._execute_event(
        event
    )

    action_executor.execute \
        .assert_called_once_with(
            SystemAction.COPY
        )


def test_execute_relative_cursor():

    (
        coordinator,
        _,
        _,
        _,
        mouse
    ) = create_coordinator()

    event = InteractionEvent(
        source=EventSource.HEAD,
        event_type=EventType.CURSOR_MOVE,
        payload={
            "mode": "relative",
            "dx": 5,
            "dy": -3
        }
    )

    coordinator._execute_event(
        event
    )

    mouse.move_relative \
        .assert_called_once_with(
            5,
            -3
        )


def test_execute_absolute_cursor():

    (
        coordinator,
        _,
        _,
        _,
        mouse
    ) = create_coordinator()

    event = InteractionEvent(
        source=EventSource.LIMB,
        event_type=EventType.CURSOR_MOVE,
        payload={
            "mode": "absolute",
            "x": 500,
            "y": 300
        }
    )

    coordinator._execute_event(
        event
    )

    mouse.move_to \
        .assert_called_once_with(
            500,
            300
        )

def test_draw_action_controls_overlay():

    (
        coordinator,
        _,
        _,
        action_executor,
        _
    ) = create_coordinator()

    overlay = MagicMock()

    coordinator.overlay_service = (
        overlay
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.DRAW
    )

    coordinator._execute_event(
        event
    )

    overlay.toggle_draw \
        .assert_called_once()

    action_executor.execute \
        .assert_not_called()


def test_erase_action_controls_overlay():

    (
        coordinator,
        _,
        _,
        action_executor,
        _
    ) = create_coordinator()

    overlay = MagicMock()

    coordinator.overlay_service = (
        overlay
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.ERASE
    )

    coordinator._execute_event(
        event
    )

    overlay.toggle_erase \
        .assert_called_once()

    action_executor.execute \
        .assert_not_called()

def test_zoom_in_action_controls_zoom_service():

    (
        coordinator,
        _,
        _,
        action_executor,
        _
    ) = create_coordinator()

    zoom_service = (
        MagicMock()
    )

    coordinator.zoom_service = (
        zoom_service
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.ZOOM_IN
    )

    coordinator._execute_event(
        event
    )

    zoom_service.zoom_in \
        .assert_called_once()

    action_executor.execute \
        .assert_not_called()


def test_zoom_out_action_controls_zoom_service():

    (
        coordinator,
        _,
        _,
        action_executor,
        _
    ) = create_coordinator()

    zoom_service = (
        MagicMock()
    )

    coordinator.zoom_service = (
        zoom_service
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.ZOOM_OUT
    )

    coordinator._execute_event(
        event
    )

    zoom_service.zoom_out \
        .assert_called_once()

    action_executor.execute \
        .assert_not_called()

def test_normal_action_shows_feedback():

    event_bus = MagicMock()

    fusion_engine = MagicMock()

    action_executor = MagicMock()

    mouse = MagicMock()

    overlay = MagicMock()

    coordinator = (
        MultimodalCoordinator(
            event_bus=event_bus,
            fusion_engine=(
                fusion_engine
            ),
            action_executor=(
                action_executor
            ),
            mouse_controller=mouse,
            overlay_service=overlay
        )
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY
    )

    coordinator._execute_event(
        event
    )

    action_executor.execute \
        .assert_called_once_with(
            SystemAction.COPY
        )

    overlay.show_feedback \
        .assert_called_once_with(
            "Copiar", feedback_type="success"
        )


def test_zoom_shows_visual_feedback():

    event_bus = MagicMock()

    fusion_engine = MagicMock()

    action_executor = MagicMock()

    mouse = MagicMock()

    overlay = MagicMock()

    zoom_service = MagicMock()

    zoom_service.zoom_in \
        .return_value = True

    zoom_service.current_zoom = (
        1.25
    )

    coordinator = (
        MultimodalCoordinator(
            event_bus=event_bus,
            fusion_engine=(
                fusion_engine
            ),
            action_executor=(
                action_executor
            ),
            mouse_controller=mouse,
            overlay_service=overlay,
            zoom_service=(
                zoom_service
            )
        )
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.ZOOM_IN
    )

    coordinator._execute_event(
        event
    )

    overlay.show_feedback \
        .assert_called_once_with(
            "Zoom 125%", feedback_type="success"
        )

def test_normal_action_plays_audio_feedback():

    event_bus = MagicMock()

    fusion_engine = MagicMock()

    action_executor = MagicMock()

    mouse = MagicMock()

    overlay = MagicMock()

    audio_feedback = MagicMock()

    coordinator = (
        MultimodalCoordinator(
            event_bus=event_bus,
            fusion_engine=(
                fusion_engine
            ),
            action_executor=(
                action_executor
            ),
            mouse_controller=mouse,
            overlay_service=overlay,
            audio_feedback_service=(
                audio_feedback
            )
        )
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY
    )

    coordinator._execute_event(
        event
    )

    audio_feedback \
        .play_success \
        .assert_called_once()


def test_cursor_movement_does_not_play_audio():

    event_bus = MagicMock()

    fusion_engine = MagicMock()

    action_executor = MagicMock()

    mouse = MagicMock()

    audio_feedback = MagicMock()

    coordinator = (
        MultimodalCoordinator(
            event_bus=event_bus,
            fusion_engine=(
                fusion_engine
            ),
            action_executor=(
                action_executor
            ),
            mouse_controller=mouse,
            audio_feedback_service=(
                audio_feedback
            )
        )
    )

    event = InteractionEvent(
        source=EventSource.HEAD,
        event_type=EventType.CURSOR_MOVE,
        payload={
            "mode": "relative",
            "dx": 5,
            "dy": 3
        }
    )

    coordinator._execute_event(
        event
    )

    audio_feedback \
        .play_success \
        .assert_not_called()

def test_execution_error_shows_error_feedback():

    event_bus = MagicMock()

    fusion_engine = MagicMock()

    action_executor = MagicMock()

    mouse = MagicMock()

    overlay = MagicMock()

    coordinator = (
        MultimodalCoordinator(
            event_bus=event_bus,
            fusion_engine=(
                fusion_engine
            ),
            action_executor=(
                action_executor
            ),
            mouse_controller=mouse,
            overlay_service=overlay
        )
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY
    )

    fusion_engine.process_events \
        .return_value = [
            event
        ]

    action_executor.execute \
        .side_effect = RuntimeError(
            "Error de prueba"
        )

    coordinator._pending_events = [
        event
    ]

    coordinator._flush()

    overlay.show_error_feedback \
        .assert_called_once_with(
            "No se pudo ejecutar la acción"
        )

def test_voice_error_status_shows_red_feedback():

    event_bus = MagicMock()
    fusion_engine = MagicMock()
    action_executor = MagicMock()
    mouse = MagicMock()
    overlay = MagicMock()

    coordinator = (
        MultimodalCoordinator(
            event_bus=event_bus,
            fusion_engine=(
                fusion_engine
            ),
            action_executor=(
                action_executor
            ),
            mouse_controller=mouse,
            overlay_service=overlay
        )
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.STATUS,
        payload={
            "level": "error",
            "message": (
                "Comando no reconocido"
            )
        }
    )

    coordinator._execute_event(
        event
    )

    overlay.show_error_feedback \
        .assert_called_once_with(
            "Comando no reconocido"
        )

def test_resolved_event_is_recorded_in_session():

    session_manager = (
        MagicMock()
    )

    (
        coordinator,
        _,
        fusion_engine,
        action_executor,
        _
    ) = create_coordinator(
        session_manager=(
            session_manager
        )
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY
    )

    fusion_engine.process_events \
        .return_value = [
            event
        ]

    coordinator._pending_events = [
        event
    ]

    coordinator._flush()

    session_manager.record_event \
        .assert_called_once_with(
            event
        )

    action_executor.execute \
        .assert_called_once_with(
            SystemAction.COPY
        )


def test_discarded_event_is_not_recorded():

    session_manager = (
        MagicMock()
    )

    (
        coordinator,
        _,
        fusion_engine,
        _,
        _
    ) = create_coordinator(
        session_manager=(
            session_manager
        )
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY
    )

    fusion_engine.process_events \
        .return_value = []

    coordinator._pending_events = [
        event
    ]

    coordinator._flush()

    session_manager.record_event \
        .assert_not_called()


def test_metrics_failure_does_not_stop_action():

    session_manager = (
        MagicMock()
    )

    session_manager.record_event \
        .side_effect = RuntimeError(
            "Error de métricas"
        )

    (
        coordinator,
        _,
        fusion_engine,
        action_executor,
        _
    ) = create_coordinator(
        session_manager=(
            session_manager
        )
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY
    )

    fusion_engine.process_events \
        .return_value = [
            event
        ]

    coordinator._pending_events = [
        event
    ]

    coordinator._flush()

    action_executor.execute \
        .assert_called_once_with(
            SystemAction.COPY
        )

def test_eraser_on_activates_overlay():

    (
        coordinator,
        _,
        _,
        action_executor,
        _
    ) = create_coordinator()

    overlay = MagicMock()

    overlay.is_active = False
    overlay.mode = None
    overlay.MODE_ERASE = "erase"

    coordinator.overlay_service = (
        overlay
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.ERASER_ON
    )

    coordinator._execute_event(
        event
    )

    overlay.toggle_erase \
        .assert_called_once()

    action_executor.execute \
        .assert_not_called()


def test_eraser_on_does_not_toggle_when_already_active():

    (
        coordinator,
        _,
        _,
        action_executor,
        _
    ) = create_coordinator()

    overlay = MagicMock()

    overlay.is_active = True
    overlay.mode = "erase"
    overlay.MODE_ERASE = "erase"

    coordinator.overlay_service = (
        overlay
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.ERASER_ON
    )

    coordinator._execute_event(
        event
    )

    overlay.toggle_erase \
        .assert_not_called()

    action_executor.execute \
        .assert_not_called()


def test_eraser_off_deactivates_overlay():

    (
        coordinator,
        _,
        _,
        action_executor,
        _
    ) = create_coordinator()

    overlay = MagicMock()

    overlay.is_active = True
    overlay.mode = "erase"
    overlay.MODE_ERASE = "erase"

    coordinator.overlay_service = (
        overlay
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.ERASER_OFF
    )

    coordinator._execute_event(
        event
    )

    overlay.toggle_erase \
        .assert_called_once()

    action_executor.execute \
        .assert_not_called()

def shutdown_action():
    return InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY,
    )


def test_stop_rejects_new_events_and_unsubscribes():
    from unittest.mock import patch

    coordinator, bus, fusion, executor, _ = create_coordinator()
    coordinator.stop()
    with patch('application.interaction.multimodal_coordinator.threading.Timer') as timer:
        # Also models a callback copied by EventBus before unsubscription.
        coordinator._receive_event(shutdown_action())
        coordinator._flush()
        coordinator._execute_event(shutdown_action())
        timer.assert_not_called()
    assert coordinator._pending_events == []
    bus.unsubscribe_all.assert_called_once_with(coordinator._receive_event)
    fusion.process_events.assert_not_called()
    executor.execute.assert_not_called()


def test_event_published_after_stop_is_not_executed():
    from infrastructure.event_bus.event_bus import EventBus
    from unittest.mock import patch

    bus = EventBus()
    executor = MagicMock()
    coordinator = MultimodalCoordinator(bus, MagicMock(), executor, MagicMock())
    coordinator.stop()
    with patch.object(coordinator, '_receive_event') as receive:
        bus.publish(shutdown_action())
        receive.assert_not_called()
    coordinator._flush()
    executor.execute.assert_not_called()


def test_stop_cancels_pending_timer_and_late_callback_is_harmless():
    from unittest.mock import patch

    coordinator, _, fusion, executor, _ = create_coordinator()
    with patch('application.interaction.multimodal_coordinator.threading.Timer') as timer:
        coordinator._receive_event(shutdown_action())
        callback = timer.call_args.args[1]
        timer.return_value.start.assert_called_once()
        coordinator.stop()
        timer.return_value.cancel.assert_called_once()
        assert coordinator._timer is None
        assert coordinator._pending_events == []
        # Timer.cancel() may race with a callback that has already started.
        callback()
    fusion.process_events.assert_not_called()
    executor.execute.assert_not_called()


def test_stop_is_idempotent_and_finalizes_tracker_once():
    tracker = MagicMock()
    coordinator, bus, _, _, _ = create_coordinator(
        interaction_outcome_tracker=tracker,
    )
    coordinator.stop()
    coordinator.stop()
    tracker.finalize_pending_drag.assert_called_once()
    bus.unsubscribe_all.assert_called_once()


def test_stop_waits_for_active_flush_before_finalizing_outcomes():
    import threading
    from unittest.mock import patch

    tracker = MagicMock()
    coordinator, bus, fusion, executor, _ = create_coordinator(
        interaction_outcome_tracker=tracker,
    )
    event = shutdown_action()
    coordinator._pending_events = [event]
    fusion.process_events.return_value = [event, event]
    entered = threading.Event()
    release = threading.Event()
    waiting = threading.Event()
    stopped = threading.Event()
    order = []
    errors = []

    def execute(action):
        entered.set()
        if not release.wait(3):
            raise AssertionError('Test did not release executor')
        order.append('execute')
        return True

    def record(*args):
        order.append('outcome')

    def finalize():
        order.append('finalize')

    real_wait_for = coordinator._condition.wait_for

    def wait_for(predicate):
        if not predicate():
            waiting.set()
        return real_wait_for(predicate)

    def stop():
        try:
            coordinator.stop()
            order.append('stop_returned')
        except BaseException as error:
            errors.append(error)
        finally:
            stopped.set()

    executor.execute.side_effect = execute
    tracker.record_action_result.side_effect = record
    tracker.finalize_pending_drag.side_effect = finalize
    flush_thread = threading.Thread(target=coordinator._flush, daemon=True)
    stop_thread = threading.Thread(target=stop, daemon=True)
    with patch.object(coordinator._condition, 'wait_for', side_effect=wait_for):
        flush_thread.start()
        try:
            assert entered.wait(3)
            stop_thread.start()
            assert waiting.wait(3)
            assert not stopped.is_set()
            tracker.finalize_pending_drag.assert_not_called()
            # Even a previously copied callback cannot enqueue during stop.
            coordinator._receive_event(event)
            assert coordinator._pending_events == []
        finally:
            release.set()
            flush_thread.join(3)
            if stop_thread.ident is not None:
                stop_thread.join(3)
    assert not flush_thread.is_alive()
    assert not stop_thread.is_alive()
    assert not errors
    assert order == ['execute', 'outcome', 'finalize', 'stop_returned']
    assert coordinator._active_flush_threads == []
    executor.execute.assert_called_once()
    tracker.finalize_pending_drag.assert_called_once()
    # Neither late callbacks nor an explicit flush execute after return.
    coordinator._receive_event(event)
    coordinator._flush()
    coordinator._execute_event(event)
    assert order == ['execute', 'outcome', 'finalize', 'stop_returned']
    bus.unsubscribe_all.assert_called_once()


def test_concurrent_stop_waits_for_single_tracker_finalization():
    import threading
    from unittest.mock import patch

    tracker = MagicMock()
    coordinator, _, _, _, _ = create_coordinator(
        interaction_outcome_tracker=tracker,
    )
    finalizing = threading.Event()
    release = threading.Event()
    waiting = threading.Event()
    second_returned = threading.Event()

    def finalize():
        finalizing.set()
        assert release.wait(3)

    real_wait_for = coordinator._condition.wait_for

    def wait_for(predicate):
        if not predicate():
            waiting.set()
        return real_wait_for(predicate)

    def second_stop():
        coordinator.stop()
        second_returned.set()

    tracker.finalize_pending_drag.side_effect = finalize
    first = threading.Thread(target=coordinator.stop, daemon=True)
    second = threading.Thread(target=second_stop, daemon=True)
    with patch.object(coordinator._condition, 'wait_for', side_effect=wait_for):
        first.start()
        try:
            assert finalizing.wait(3)
            second.start()
            assert waiting.wait(3)
            assert not second_returned.is_set()
        finally:
            release.set()
            first.join(3)
            if second.ident is not None:
                second.join(3)
    assert not first.is_alive()
    assert not second.is_alive()
    assert second_returned.is_set()
    tracker.finalize_pending_drag.assert_called_once()


def test_flush_failure_does_not_leave_stop_waiting():
    import pytest

    tracker = MagicMock()
    coordinator, _, fusion, _, _ = create_coordinator(
        interaction_outcome_tracker=tracker,
    )
    coordinator._pending_events = [shutdown_action()]
    fusion.process_events.side_effect = RuntimeError('Fusion failed')
    with pytest.raises(RuntimeError, match='Fusion failed'):
        coordinator._flush()
    assert coordinator._active_flush_threads == []
    coordinator.stop()
    tracker.finalize_pending_drag.assert_called_once()


def test_stop_from_flush_callback_raises_instead_of_deadlocking():
    import pytest

    coordinator, _, fusion, _, _ = create_coordinator()
    coordinator._pending_events = [shutdown_action()]

    def process(events):
        with pytest.raises(RuntimeError, match='callback activo'):
            coordinator.stop()
        return []

    fusion.process_events.side_effect = process
    coordinator._flush()
    assert not coordinator._stopped
    coordinator.stop()


def test_stop_stays_idempotent_when_tracker_finalization_fails():
    tracker = MagicMock()
    tracker.finalize_pending_drag.side_effect = RuntimeError('Tracker failed')
    coordinator, _, _, _, _ = create_coordinator(
        interaction_outcome_tracker=tracker,
    )
    coordinator.stop()
    coordinator.stop()
    tracker.finalize_pending_drag.assert_called_once()


def test_stop_waits_for_all_overlapping_flushes():
    import threading
    from unittest.mock import patch

    tracker = MagicMock()
    coordinator, _, fusion, _, _ = create_coordinator(
        interaction_outcome_tracker=tracker,
    )
    event = shutdown_action()
    entered = [threading.Event(), threading.Event()]
    release = [threading.Event(), threading.Event()]
    waiting = threading.Event()
    stopped = threading.Event()
    errors = []
    index_lock = threading.Lock()
    call_index = [0]

    def process(events):
        with index_lock:
            index = call_index[0]
            call_index[0] += 1
        entered[index].set()
        if not release[index].wait(3):
            raise AssertionError('Test did not release fusion')
        return []

    def flush():
        try:
            coordinator._flush()
        except BaseException as error:
            errors.append(error)

    real_wait_for = coordinator._condition.wait_for

    def wait_for(predicate):
        if not predicate():
            waiting.set()
        return real_wait_for(predicate)

    def stop():
        coordinator.stop()
        stopped.set()

    fusion.process_events.side_effect = process
    workers = [threading.Thread(target=flush, daemon=True) for _ in range(2)]
    closer = threading.Thread(target=stop, daemon=True)
    with patch.object(coordinator._condition, 'wait_for', side_effect=wait_for):
        try:
            for index, worker in enumerate(workers):
                with coordinator._lock:
                    coordinator._pending_events = [event]
                worker.start()
                assert entered[index].wait(3)
            closer.start()
            assert waiting.wait(3)
            release[0].set()
            workers[0].join(3)
            assert not workers[0].is_alive()
            assert not stopped.is_set()
            tracker.finalize_pending_drag.assert_not_called()
        finally:
            for signal in release:
                signal.set()
            for worker in workers:
                if worker.ident is not None:
                    worker.join(3)
            if closer.ident is not None:
                closer.join(3)
    assert not errors
    assert all(not worker.is_alive() for worker in workers)
    assert not closer.is_alive()
    assert stopped.is_set()
    tracker.finalize_pending_drag.assert_called_once()


def test_stop_from_finalizer_raises_instead_of_waiting_for_itself():
    import pytest

    tracker = MagicMock()
    coordinator, _, _, _, _ = create_coordinator(
        interaction_outcome_tracker=tracker,
    )

    def finalize():
        with pytest.raises(RuntimeError, match='callback activo'):
            coordinator.stop()

    tracker.finalize_pending_drag.side_effect = finalize
    coordinator.stop()
    coordinator.stop()
    tracker.finalize_pending_drag.assert_called_once()
