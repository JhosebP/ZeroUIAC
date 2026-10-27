import threading
from collections import deque
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from application.interaction.action_executor import ActionExecutor
from application.interaction.dictation_service import DictationService
from application.interaction.multimodal_coordinator import MultimodalCoordinator
from application.interaction.multimodal_vision_service import MultimodalVisionService
from application.interaction.system_mode_manager import SystemModeManager
from application.interaction.voice_control_service import VoiceControlService
from domain.commands.system_actions import SystemAction
from domain.events.event_types import EventSource, EventType
from domain.events.interaction_event import InteractionEvent
from infrastructure.event_bus.event_bus import EventBus
from modules.adaptation.adaptive_action_applier import AdaptiveActionApplier
from modules.adaptation.adaptive_runtime_controller import AdaptiveRuntimeController
from modules.adaptation.interaction_outcome_tracker import InteractionOutcomeTracker
from modules.adaptation.session_manager import SessionManager
from modules.multimodal.fusion_engine import FusionEngine
from modules.voice.voice_commands import SYSTEM_CONTROL_COMMANDS, VOICE_COMMANDS, VOICE_GRAMMAR
from modules.voice.voice_mode import VoiceModeManager
from presentation.overlay.annotation_overlay import AnnotationOverlay
from presentation.overlay.command_help import get_command_groups


@pytest.fixture
def runtime(monkeypatch):
    monkeypatch.setattr(
        'application.interaction.multimodal_coordinator.threading.Timer', MagicMock(),
    )
    state = SystemModeManager()
    bus = EventBus()
    overlay = AnnotationOverlay(system_mode_manager=state)
    tracker = InteractionOutcomeTracker()
    session = SessionManager()
    session.start_session()
    mouse, keyboard = MagicMock(), MagicMock()
    executor = ActionExecutor(mouse, keyboard)
    modes = VoiceModeManager()
    dictation_recognizer = MagicMock()
    text = MagicMock()
    text.write_text.return_value = True
    dictation = DictationService(dictation_recognizer, text, modes)
    voice = VoiceControlService(
        bus, SimpleNamespace(), dictation, modes, system_mode_manager=state,
    )
    coordinator = MultimodalCoordinator(
        bus, FusionEngine(), executor, mouse, overlay_service=overlay,
        session_manager=session, interaction_outcome_tracker=tracker,
        system_mode_manager=state,
    )
    result = SimpleNamespace(
        state=state, bus=bus, overlay=overlay, tracker=tracker, session=session,
        mouse=mouse, keyboard=keyboard, executor=executor, modes=modes,
        dictation_recognizer=dictation_recognizer, text=text, voice=voice,
        coordinator=coordinator,
    )
    yield result
    coordinator.stop()


def say(runtime, phrase, flush=True):
    recognizer = MagicMock()
    recognizer.process_audio.return_value = phrase
    result = runtime.voice.process_audio(b'audio', recognizer)
    if flush:
        runtime.coordinator._flush()
    return result


def event(source, action=None):
    return InteractionEvent(
        source=source,
        event_type=EventType.ACTION if action else EventType.CURSOR_MOVE,
        action=action,
        payload={} if action else {'mode': 'relative', 'dx': 5, 'dy': 3},
    )


@pytest.mark.parametrize('phrase', list(SYSTEM_CONTROL_COMMANDS))
def test_system_phrases_exist_in_closed_grammar(phrase):
    assert VOICE_GRAMMAR.count(phrase) == 1
    assert phrase not in VOICE_COMMANDS


@pytest.mark.parametrize('phrase', list(SYSTEM_CONTROL_COMMANDS))
def test_system_controls_are_yellow_and_do_not_feed_metrics(runtime, phrase):
    if phrase == 'zero ui activar':
        runtime.state.suspend()
    assert say(runtime, phrase) == phrase
    assert runtime.overlay.feedback_text == SYSTEM_CONTROL_COMMANDS[phrase]
    assert runtime.overlay.feedback_type == 'system_control'
    assert runtime.session.get_snapshot()['metrics']['total_events'] == 0
    assert runtime.tracker.snapshot()['action_attempts'] == 0
    assert runtime.tracker.snapshot()['cursor_samples'] == 0
    assert not runtime.keyboard.mock_calls
    assert not runtime.mouse.mock_calls


def test_suspend_and_activate_are_idempotent(runtime):
    say(runtime, 'zero ui suspender')
    assert runtime.state.is_suspended()
    assert say(runtime, 'zero ui suspender') is None
    assert runtime.state.is_suspended()
    assert say(runtime, 'zero ui activar') == 'zero ui activar'
    assert runtime.state.is_active()
    assert say(runtime, 'zero ui activar') == 'zero ui activar'
    assert runtime.state.is_active()
    runtime.state.suspend()
    runtime.state.suspend()
    runtime.state.activate()
    runtime.state.activate()
    assert runtime.state.is_active()


@pytest.mark.parametrize('source,action', [
    (EventSource.HEAD, None),
    (EventSource.LIMB, None),
    (EventSource.GESTURE, SystemAction.DRAW),
    (EventSource.VOICE, SystemAction.ENTER),
    (EventSource.VOICE, SystemAction.LEFT_CLICK),
    (EventSource.HEAD, SystemAction.ZOOM_IN),
])
def test_suspended_channels_are_ignored_without_metrics(runtime, source, action):
    runtime.state.suspend()
    ignored = event(source, action)
    runtime.bus.publish(ignored)
    runtime.coordinator._execute_event(ignored)
    runtime.coordinator._flush()
    assert runtime.coordinator._pending_events == []
    assert runtime.session.get_snapshot()['metrics']['total_events'] == 0
    assert runtime.tracker.snapshot()['action_attempts'] == 0
    assert runtime.tracker.snapshot()['cursor_samples'] == 0
    assert not runtime.overlay.is_active
    assert not runtime.keyboard.mock_calls
    assert not runtime.mouse.mock_calls


@pytest.mark.parametrize('phrase', [
    'clic', 'enter', 'activar dictado', 'activar zoom', 'acercar',
    'zero ui mostrar comandos', 'zero ui ocultar comandos', None,
])
def test_only_activate_is_accepted_while_suspended(runtime, phrase):
    say(runtime, 'zero ui suspender')
    feedback_version = runtime.overlay._feedback_version
    assert say(runtime, phrase) is None
    assert runtime.state.is_suspended()
    assert runtime.overlay._feedback_version == feedback_version
    assert runtime.session.get_snapshot()['metrics']['total_events'] == 0
    assert not runtime.keyboard.mock_calls
    assert not runtime.mouse.mock_calls
    assert not runtime.modes.is_dictation_mode()


def test_activation_restores_voice_and_cursor_processing(runtime):
    say(runtime, 'zero ui suspender')
    assert say(runtime, 'enter') is None
    say(runtime, 'zero ui activar')
    assert say(runtime, 'enter') == 'enter'
    runtime.keyboard.enter.assert_called_once()
    runtime.bus.publish(event(EventSource.HEAD))
    runtime.coordinator._flush()
    runtime.mouse.move_relative.assert_called_once_with(5, 3)
    assert runtime.tracker.snapshot()['action_successes'] == 1


def test_pending_events_are_discarded_even_after_reactivation(runtime):
    from dataclasses import replace
    import time

    old_event = replace(event(EventSource.VOICE, SystemAction.ENTER), timestamp=time.monotonic() - 1)
    runtime.bus.publish(old_event)
    assert runtime.coordinator._pending_events
    say(runtime, 'zero ui suspender', flush=False)
    say(runtime, 'zero ui activar')
    runtime.bus.publish(old_event)  # A producer delayed across the transition.
    runtime.coordinator._flush()
    runtime.keyboard.enter.assert_not_called()
    assert runtime.session.get_snapshot()['metrics']['total_events'] == 0


def test_already_resolving_batch_cannot_execute_after_suspend_resume(runtime):
    entered, release = threading.Event(), threading.Event()
    old_event = event(EventSource.VOICE, SystemAction.ENTER)

    def resolve(events):
        entered.set()
        assert release.wait(3)
        return events

    runtime.coordinator.fusion_engine.process_events = resolve
    runtime.coordinator._pending_events = [old_event]
    worker = threading.Thread(target=runtime.coordinator._flush, daemon=True)
    worker.start()
    try:
        assert entered.wait(3)
        say(runtime, 'zero ui suspender', flush=False)
        say(runtime, 'zero ui activar', flush=False)
    finally:
        release.set()
        worker.join(3)
    assert not worker.is_alive()
    runtime.keyboard.enter.assert_not_called()
    assert runtime.session.get_snapshot()['metrics']['total_events'] == 0


def test_suspend_waits_for_admitted_execution_without_deadlock(runtime):
    entered, release, requested, suspended = (threading.Event() for _ in range(4))

    def press():
        entered.set()
        assert release.wait(3)

    def suspend():
        requested.set()
        runtime.state.suspend()
        suspended.set()

    runtime.keyboard.enter.side_effect = press
    runtime.coordinator._pending_events = [event(EventSource.VOICE, SystemAction.ENTER)]
    worker = threading.Thread(target=runtime.coordinator._flush, daemon=True)
    closer = threading.Thread(target=suspend, daemon=True)
    worker.start()
    try:
        assert entered.wait(3)
        closer.start()
        assert requested.wait(3)
        assert not suspended.is_set()
    finally:
        release.set()
        worker.join(3)
        if closer.ident is not None:
            closer.join(3)
    assert not worker.is_alive() and not closer.is_alive()
    assert suspended.is_set()
    runtime.coordinator._execute_event(event(EventSource.VOICE, SystemAction.ENTER))
    runtime.keyboard.enter.assert_called_once()


def test_controls_work_from_dictation_without_being_written(runtime):
    runtime.voice.dictation_service.start()
    runtime.dictation_recognizer.process_audio.return_value = 'zero ui suspender'
    assert say(runtime, 'ignored by dictation') == 'zero ui suspender'
    assert runtime.state.is_suspended()
    assert runtime.modes.is_dictation_mode()
    runtime.text.write_text.assert_not_called()
    assert say(runtime, 'zero ui activar') == 'zero ui activar'
    assert runtime.state.is_active()
    runtime.dictation_recognizer.process_audio.return_value = 'enter'
    assert say(runtime, 'dictation') == 'enter'
    runtime.text.write_text.assert_called_once_with('enter')
    runtime.keyboard.enter.assert_not_called()


def test_panel_show_hide_is_idempotent_and_suspension_preserves_it(runtime):
    say(runtime, 'zero ui mostrar comandos')
    version = runtime.overlay._commands_version
    assert runtime.overlay.commands_visible
    say(runtime, 'zero ui mostrar comandos')
    assert runtime.overlay._commands_version == version
    say(runtime, 'zero ui suspender')
    assert runtime.overlay.commands_visible
    assert say(runtime, 'zero ui ocultar comandos') is None
    assert runtime.overlay.commands_visible
    say(runtime, 'zero ui activar')
    say(runtime, 'zero ui ocultar comandos')
    assert not runtime.overlay.commands_visible
    version = runtime.overlay._commands_version
    say(runtime, 'zero ui ocultar comandos')
    assert runtime.overlay._commands_version == version


def test_catalog_has_three_groups_and_uses_live_command_sources(monkeypatch):
    groups = get_command_groups()
    assert len(groups) == 3
    modes, execution, physical = (entries for _, entries in groups)
    assert all(phrase in modes for phrase in SYSTEM_CONTROL_COMMANDS)
    assert all(phrase in modes for phrase in DictationService.EXIT_PHRASES)
    assert any('dibujar' in entry and 'alterna' in entry for entry in modes)
    assert set(execution) == set(VOICE_COMMANDS) - {'dibujar'}
    assert 'enter' in execution
    assert any('Índice y medio' in entry for entry in physical)
    assert any('anular' in entry for entry in physical)
    monkeypatch.setattr('presentation.overlay.command_help.VOICE_COMMANDS', VOICE_COMMANDS + ['test command'])
    assert 'test command' in get_command_groups()[1][1]


def test_canvas_panel_is_rendered_once_without_new_windows(runtime, monkeypatch):
    overlay = runtime.overlay
    overlay._canvas = MagicMock()
    overlay._root = MagicMock()
    monkeypatch.setattr(
        'presentation.overlay.annotation_overlay.ctypes.windll.user32.GetSystemMetrics',
        lambda metric: 1080 if metric == 1 else 1920,
    )
    create_window = MagicMock()
    monkeypatch.setattr('presentation.overlay.annotation_overlay.tk.Tk', create_window)
    overlay.show_commands()
    overlay._sync_commands_panel()
    overlay.show_commands()
    overlay._sync_commands_panel()
    overlay._canvas.create_rectangle.assert_called_once()
    assert overlay._canvas.create_text.call_count == 7
    overlay.hide_commands()
    overlay._sync_commands_panel()
    overlay.hide_commands()
    overlay._sync_commands_panel()
    assert not overlay.commands_visible
    assert overlay._canvas.create_rectangle.call_count == 1
    create_window.assert_not_called()
    overlay._root.focus_force.assert_not_called()


def test_suspended_overlay_does_not_draw_and_panel_stays_visible(runtime, monkeypatch):
    overlay = runtime.overlay
    overlay.toggle_draw()
    overlay.show_commands()
    overlay._canvas = MagicMock()
    overlay._root = MagicMock()
    monkeypatch.setattr(overlay, '_render_commands', MagicMock())
    draw = MagicMock()
    monkeypatch.setattr(overlay, '_draw', draw)
    position = MagicMock()
    monkeypatch.setattr('presentation.overlay.annotation_overlay.pyautogui.position', position)
    runtime.state.suspend()
    overlay._tick()
    draw.assert_not_called()
    position.assert_not_called()
    assert overlay.commands_visible
    overlay._root.withdraw.assert_not_called()


@pytest.mark.parametrize('action', [SystemAction.DRAW, SystemAction.ERASE])
def test_physical_gestures_use_green_but_voice_modes_use_blue(runtime, action):
    runtime.bus.publish(event(EventSource.GESTURE, action))
    runtime.coordinator._flush()
    assert runtime.overlay.feedback_type == 'success'
    assert runtime.tracker.snapshot()['action_successes'] == 0
    say(runtime, 'activar borrador')
    assert runtime.overlay.feedback_type == 'mode'


def test_yellow_rendering_keeps_existing_color_semantics(runtime, monkeypatch):
    overlay = runtime.overlay
    overlay._canvas = MagicMock()
    overlay._root = MagicMock()
    monkeypatch.setattr(
        'presentation.overlay.annotation_overlay.ctypes.windll.user32.GetSystemMetrics',
        MagicMock(return_value=1920),
    )
    overlay.show_feedback('ZeroUI activado', feedback_type='system_control')
    assert overlay.feedback_type == 'system_control'
    overlay._render_feedback(overlay.feedback_text, overlay.feedback_type)
    assert overlay._canvas.create_rectangle.call_args.kwargs['fill'] == '#F9D65C'
    assert overlay.feedback_duration == 1.5


@pytest.mark.parametrize('phrase', list(SYSTEM_CONTROL_COMMANDS))
def test_visual_failure_does_not_stop_controls(runtime, monkeypatch, phrase):
    if phrase == 'zero ui activar':
        runtime.state.suspend()
    monkeypatch.setattr(runtime.overlay, 'show_feedback', MagicMock(side_effect=RuntimeError('UI failed')))
    assert say(runtime, phrase) == phrase
    assert runtime.state.is_suspended() == (phrase == 'zero ui suspender')


def test_help_render_failure_does_not_stop_overlay_tick(runtime, monkeypatch):
    runtime.overlay._canvas = MagicMock()
    runtime.overlay._root = MagicMock()
    runtime.overlay.show_commands()
    monkeypatch.setattr(runtime.overlay, '_render_commands', MagicMock(side_effect=RuntimeError('Canvas failed')))
    runtime.overlay._tick()
    runtime.overlay._root.after.assert_called_once()


def test_general_controls_and_suspended_input_cannot_trigger_adaptation(runtime):
    clock = [0.0]
    adaptive = AdaptiveRuntimeController(
        runtime.session, AdaptiveActionApplier(), min_user_events=5,
        clock=lambda: clock[0],
    )
    adaptive.step()
    epsilon = adaptive.q_agent.epsilon
    for phrase in SYSTEM_CONTROL_COMMANDS:
        say(runtime, phrase)
    say(runtime, 'zero ui suspender')
    for _ in range(10):
        runtime.bus.publish(event(EventSource.HEAD))
        say(runtime, 'enter')
    clock[0] = 30.0
    assert adaptive.step() is None
    assert adaptive.q_agent.epsilon == epsilon
    assert adaptive.q_agent.get_q_table_snapshot() == {}
    assert runtime.session.get_snapshot()['metrics']['total_events'] == 0


def test_vision_skips_perception_and_resets_temporal_state_while_suspended(runtime):
    service = MultimodalVisionService.__new__(MultimodalVisionService)
    service.system_mode_manager = runtime.state
    service.head_mapper = MagicMock()
    service.head_zoom_detector = MagicMock()
    service.face_tracker = MagicMock()
    service.hand_tracker = MagicMock()
    service.limb_mapper = MagicMock()
    service.gesture_detector = MagicMock()
    service.pose_history = deque([{'yaw': 12}])
    runtime.state.suspend()
    service._process_head(MagicMock())
    service._process_limb(MagicMock())
    service.face_tracker.process_frame.assert_not_called()
    service.hand_tracker.process_frame.assert_not_called()
    service.head_mapper.reset.assert_called_once()
    service.limb_mapper.reset.assert_called_once()
    service.gesture_detector.reset.assert_called_once()
    assert not service.pose_history


def test_generation_rejects_old_work_even_when_windows_clock_has_not_advanced():
    state = SystemModeManager(clock=lambda: 10.0)
    old_generation = state.generation
    state.suspend()
    state.activate()
    with state.processing(timestamp=10.0, generation=old_generation) as admitted:
        assert not admitted
    with state.processing(timestamp=10.0, generation=state.generation) as admitted:
        assert admitted


def test_head_zoom_gesture_keeps_green_and_real_zoom_percentage(runtime):
    from application.interaction.zoom_service import ZoomService

    magnification = MagicMock()
    magnification.set_zoom.return_value = True
    runtime.mouse.get_position.return_value = (400, 300)
    runtime.mouse.get_screen_size.return_value = (1920, 1080)
    runtime.coordinator.zoom_service = ZoomService(magnification, runtime.mouse)
    runtime.bus.publish(event(EventSource.HEAD, SystemAction.ZOOM_IN))
    runtime.coordinator._flush()
    assert runtime.overlay.feedback_type == 'success'
    assert runtime.overlay.feedback_text == 'Zoom 125%'


@pytest.mark.parametrize('phrase,method', [
    ('zero ui mostrar comandos', 'show_commands'),
    ('zero ui ocultar comandos', 'hide_commands'),
])
def test_panel_operation_failure_is_isolated(runtime, monkeypatch, phrase, method):
    monkeypatch.setattr(runtime.overlay, method, MagicMock(side_effect=RuntimeError('UI failed')))
    assert say(runtime, phrase) == phrase
    assert say(runtime, 'enter') == 'enter'
    runtime.keyboard.enter.assert_called_once()
