from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from application.interaction.dictation_service import DictationService
from application.interaction.multimodal_coordinator import MultimodalCoordinator
from application.interaction.voice_control_service import VoiceControlService
from domain.commands.system_actions import SystemAction
from domain.events.event_types import EventType
from infrastructure.event_bus.event_bus import EventBus
from modules.adaptation.interaction_outcome_tracker import InteractionOutcomeTracker
from modules.multimodal.fusion_engine import FusionEngine
from modules.voice.voice_mode import VoiceModeManager
from presentation.overlay.annotation_overlay import AnnotationOverlay


@pytest.fixture
def feedback_runtime(monkeypatch):
    # Exercise the real event and overlay state path without UI or timers.
    monkeypatch.setattr(
        'application.interaction.multimodal_coordinator.threading.Timer', MagicMock(),
    )
    bus = EventBus()
    overlay = AnnotationOverlay()
    tracker = InteractionOutcomeTracker()
    executor = MagicMock()
    executor.execute.return_value = True
    modes = VoiceModeManager()
    dictation_recognizer = MagicMock()
    dictation = DictationService(dictation_recognizer, MagicMock(), modes)
    service = VoiceControlService(
        bus, SimpleNamespace(), dictation, modes,
    )
    coordinator = MultimodalCoordinator(
        bus, FusionEngine(), executor, MagicMock(),
        overlay_service=overlay, interaction_outcome_tracker=tracker,
    )
    events = []
    bus.subscribe_all(events.append)
    runtime = SimpleNamespace(
        service=service, coordinator=coordinator, overlay=overlay,
        tracker=tracker, executor=executor, modes=modes,
        dictation_recognizer=dictation_recognizer, events=events,
    )
    yield runtime
    coordinator.stop()


def command(runtime, text):
    recognizer = MagicMock()
    recognizer.process_audio.return_value = text
    result = runtime.service.process_audio(b'audio', recognizer)
    runtime.coordinator._flush()
    return result


@pytest.mark.parametrize('text,label,action', [
    ('enter', 'Enter ejecutado', SystemAction.ENTER),
    ('copiar', 'Copiar', SystemAction.COPY),
])
def test_execution_uses_general_success_feedback(feedback_runtime, text, label, action):
    runtime = feedback_runtime
    assert command(runtime, text) == text
    runtime.executor.execute.assert_called_once_with(action)
    assert runtime.overlay.feedback_text == label
    assert runtime.overlay.feedback_type == 'success'
    assert runtime.overlay.feedback_duration == 1.5
    assert runtime.tracker.snapshot()['action_successes'] == 1


@pytest.mark.parametrize('text,label', [
    ('activar dictado', 'Dictado activado'),
    ('activar zoom', 'Zoom activado'),
    ('desactivar zoom', 'Zoom desactivado'),
    ('activar borrador', 'Borrador activado'),
    ('desactivar borrador', 'Borrador desactivado'),
])
def test_mode_commands_use_blue_feedback_without_technical_actions(feedback_runtime, text, label):
    runtime = feedback_runtime
    if text == 'desactivar zoom':
        runtime.service.zoom_mode_manager.enable()
    if text == 'desactivar borrador':
        runtime.overlay.toggle_erase()

    assert command(runtime, text) == text
    assert runtime.overlay.feedback_text == label
    assert runtime.overlay.feedback_type == 'mode'
    assert runtime.tracker.snapshot()['action_attempts'] == 0
    assert runtime.tracker.snapshot()['action_successes'] == 0
    runtime.executor.execute.assert_not_called()

    if 'dictado' in text:
        assert runtime.modes.is_dictation_mode()
    elif 'zoom' in text:
        assert runtime.service.zoom_mode_manager.is_enabled() == text.startswith('activar')
    else:
        assert runtime.overlay.is_active == text.startswith('activar')
    if 'dictado' in text or 'zoom' in text:
        assert runtime.events[-1].event_type == EventType.STATUS
        assert runtime.events[-1].action is None
        assert runtime.events[-1].payload['level'] == 'mode'


@pytest.mark.parametrize('phrase', ['desactivar dictado', 'finalizar dictado', 'terminar dictado'])
def test_dictation_exit_reports_mode_disabled(feedback_runtime, phrase):
    runtime = feedback_runtime
    runtime.service.dictation_service.start()
    runtime.dictation_recognizer.process_audio.return_value = phrase
    command_recognizer = MagicMock()

    result = runtime.service.process_audio(b'audio', command_recognizer)
    runtime.coordinator._flush()

    assert result == DictationService.EXIT_PHRASE
    assert runtime.modes.is_command_mode()
    assert runtime.overlay.feedback_text == 'Dictado desactivado'
    assert runtime.overlay.feedback_type == 'mode'
    assert runtime.events[-1].event_type == EventType.STATUS
    runtime.executor.execute.assert_not_called()
    assert runtime.tracker.snapshot()['action_successes'] == 0


@pytest.mark.parametrize('text,active,inactive', [
    ('dibujar', 'Dibujo activado', 'Dibujo desactivado'),
])
def test_draw_toggle_reports_actual_mode_without_counting_actions(feedback_runtime, text, active, inactive):
    runtime = feedback_runtime
    command(runtime, text)
    assert runtime.overlay.is_active
    assert runtime.overlay.feedback_text == active
    assert runtime.overlay.feedback_type == 'mode'
    command(runtime, text)
    assert not runtime.overlay.is_active
    assert runtime.overlay.feedback_text == inactive
    assert runtime.overlay.feedback_type == 'mode'
    assert runtime.tracker.snapshot()['action_attempts'] == 0
    runtime.executor.execute.assert_not_called()


@pytest.mark.parametrize('text', ['enter', 'activar zoom', 'activar dictado', 'activar borrador', 'dibujar'])
def test_visual_failure_does_not_interrupt_command(feedback_runtime, monkeypatch, text):
    runtime = feedback_runtime
    monkeypatch.setattr(runtime.overlay, 'show_feedback', MagicMock(side_effect=RuntimeError('UI failed')))
    assert command(runtime, text) == text
    if text == 'enter':
        runtime.executor.execute.assert_called_once_with(SystemAction.ENTER)
        assert runtime.tracker.snapshot()['action_successes'] == 1
    elif text == 'activar zoom':
        assert runtime.service.zoom_mode_manager.is_enabled()
    elif text == 'activar dictado':
        assert runtime.modes.is_dictation_mode()
    else:
        assert runtime.overlay.is_active


def test_failed_enter_retains_error_feedback(feedback_runtime):
    runtime = feedback_runtime
    runtime.executor.execute.return_value = False
    command(runtime, 'enter')
    assert runtime.overlay.feedback_type == 'error'
    assert runtime.overlay.feedback_text == 'Acción no ejecutada'
    assert runtime.tracker.snapshot()['action_failures'] == 1


def test_failed_mode_status_publication_does_not_undo_mode(feedback_runtime, monkeypatch):
    runtime = feedback_runtime
    monkeypatch.setattr(runtime.service.event_bus, 'publish', MagicMock(side_effect=RuntimeError('UI path failed')))
    assert command(runtime, 'activar dictado') == 'activar dictado'
    assert runtime.modes.is_dictation_mode()


@pytest.mark.parametrize('kind,background,foreground', [
    ('success', '#245C45', 'white'),
    ('mode', '#87CEFA', '#102A43'),
    ('error', '#B3261E', 'white'),
])
def test_overlay_renders_semantic_color_with_same_duration(monkeypatch, kind, background, foreground):
    overlay = AnnotationOverlay()
    overlay._canvas = MagicMock()
    overlay._root = MagicMock()
    monkeypatch.setattr(
        'presentation.overlay.annotation_overlay.ctypes.windll.user32.GetSystemMetrics',
        MagicMock(return_value=1920),
    )
    monkeypatch.setattr('presentation.overlay.annotation_overlay.time.monotonic', lambda: 100.0)
    overlay.show_feedback('Mensaje', feedback_type=kind)
    assert overlay.feedback_type == kind
    assert overlay._feedback_until == 101.5
    overlay._render_feedback(overlay.feedback_text, overlay.feedback_type)
    assert overlay._canvas.create_rectangle.call_args.kwargs['fill'] == background
    assert overlay._canvas.create_text.call_args.kwargs['fill'] == foreground
