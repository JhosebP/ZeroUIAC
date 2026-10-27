from types import SimpleNamespace
from unittest.mock import MagicMock

from application.interaction.voice_control_service import (
    VoiceControlService
)

from application.interaction.dictation_service import (
    DictationService
)

from domain.commands.system_actions import (
    SystemAction
)

from domain.events.event_types import (
    EventSource,
    EventType
)

from modules.voice.voice_mode import (
    VoiceModeManager
)

from modules.voice.recognizer import (
    VoiceRecognizer
)

from domain.events.event_types import (
    EventType
)



def create_service():

    event_bus = MagicMock()

    profile = SimpleNamespace(
        microphone_sample_rate=16000,
        microphone_gain=1.0
    )

    mode_manager = VoiceModeManager()

    dictation_service = MagicMock()

    service = VoiceControlService(
        event_bus=event_bus,
        calibration_profile=profile,
        dictation_service=dictation_service,
        voice_mode_manager=mode_manager
    )

    return (
        service,
        event_bus,
        dictation_service,
        mode_manager
    )


def test_normal_command_publishes_event():

    (
        service,
        event_bus,
        _,
        _
    ) = create_service()

    recognizer = MagicMock()

    recognizer.process_audio.return_value = (
        "copiar"
    )

    result = service.process_audio(
        b"audio",
        recognizer
    )

    assert result == "copiar"

    event_bus.publish \
        .assert_called_once()

    event = (
        event_bus
        .publish
        .call_args
        .args[0]
    )

    assert (
        event.source
        == EventSource.VOICE
    )

    assert (
        event.event_type
        == EventType.ACTION
    )

    assert (
        event.action
        == SystemAction.COPY
    )


def test_activate_dictation_starts_service():

    (
        service,
        event_bus,
        dictation_service,
        _
    ) = create_service()

    recognizer = MagicMock()

    recognizer.process_audio.return_value = (
        "activar dictado"
    )

    result = service.process_audio(
        b"audio",
        recognizer
    )

    assert result == "activar dictado"

    dictation_service.start \
        .assert_called_once()

    recognizer.reset \
        .assert_called_once()

    event_bus.publish.assert_called_once()
    event = event_bus.publish.call_args.args[0]
    assert event.event_type == EventType.STATUS
    assert event.payload["level"] == "mode"
    assert event.payload["message"] == "Dictado activado"


def test_dictation_mode_routes_audio_to_dictation():

    (
        service,
        event_bus,
        dictation_service,
        mode_manager
    ) = create_service()

    recognizer = MagicMock()

    mode_manager.activate_dictation()

    dictation_service.process_audio \
        .return_value = (
            "hola mundo"
        )

    result = service.process_audio(
        b"audio",
        recognizer
    )

    assert result == "hola mundo"

    dictation_service.process_audio \
        .assert_called_once_with(
            b"audio"
        )

    recognizer.process_audio \
        .assert_not_called()

    event_bus.publish \
        .assert_not_called()


def test_exit_dictation_resets_command_recognizer():

    (
        service,
        _,
        dictation_service,
        mode_manager
    ) = create_service()

    recognizer = MagicMock()

    mode_manager.activate_dictation()

    dictation_service.process_audio \
        .return_value = (
            DictationService.EXIT_PHRASE
        )

    result = service.process_audio(
        b"audio",
        recognizer
    )

    assert (
        result
        == DictationService.EXIT_PHRASE
    )

    recognizer.reset \
        .assert_called_once()


def test_zoom_in_command_is_published():

    (
        service,
        event_bus,
        _,
        _
    ) = create_service()

    recognizer = MagicMock()

    recognizer.process_audio.return_value = (
        "acercar"
    )

    result = service.process_audio(
        b"audio",
        recognizer
    )

    assert result == "acercar"

    event_bus.publish \
        .assert_called_once()

    published_event = (
        event_bus.publish
        .call_args
        .args[0]
    )

    assert (
        published_event.source
        == EventSource.VOICE
    )

    assert (
        published_event.event_type
        == EventType.ACTION
    )

    assert (
        published_event.action
        == SystemAction.ZOOM_IN
    )

def test_unknown_command_publishes_error_status():

    (
        service,
        event_bus,
        _,
        _
    ) = create_service()

    recognizer = MagicMock()

    recognizer.process_audio \
        .return_value = None

    recognizer.last_status = (
        VoiceRecognizer.STATUS_UNKNOWN
    )

    result = service.process_audio(
        b"audio",
        recognizer
    )

    assert result is None

    event_bus.publish \
        .assert_called_once()

    event = (
        event_bus.publish
        .call_args
        .args[0]
    )

    assert (
        event.event_type
        == EventType.STATUS
    )

    assert (
        event.payload["level"]
        == "error"
    )

    assert (
        event.payload["message"]
        == "Comando no reconocido"
    )


def test_partial_audio_does_not_publish_error():

    (
        service,
        event_bus,
        _,
        _
    ) = create_service()

    recognizer = MagicMock()

    recognizer.process_audio \
        .return_value = None

    recognizer.last_status = (
        VoiceRecognizer.STATUS_PARTIAL
    )

    result = service.process_audio(
        b"audio",
        recognizer
    )

    assert result is None

    event_bus.publish \
        .assert_not_called()

def test_enter_command_publishes_execution_event():
    service, event_bus, dictation, mode_manager = create_service()
    recognizer = MagicMock()
    recognizer.process_audio.return_value = "enter"

    assert service.process_audio(b"audio", recognizer) == "enter"
    event_bus.publish.assert_called_once()
    event = event_bus.publish.call_args.args[0]
    assert event.source == EventSource.VOICE
    assert event.event_type == EventType.ACTION
    assert event.action == SystemAction.ENTER
    assert event.conflict_key == "action"
    assert mode_manager.is_command_mode()
    dictation.process_audio.assert_not_called()


def test_enter_in_dictation_remains_text_without_system_action():
    service, event_bus, _, mode_manager = create_service()
    command_recognizer = MagicMock()
    dictation_recognizer = MagicMock()
    dictation_recognizer.process_audio.return_value = "enter"
    text_controller = MagicMock()
    text_controller.write_text.return_value = True
    service.dictation_service = DictationService(
        dictation_recognizer, text_controller, mode_manager,
    )
    service.dictation_service.start()

    assert service.process_audio(b"audio", command_recognizer) == "enter"
    text_controller.write_text.assert_called_once_with("enter")
    command_recognizer.process_audio.assert_not_called()
    event_bus.publish.assert_not_called()
    assert mode_manager.is_dictation_mode()


def test_enter_voice_to_keyboard_records_success_and_failure():
    from unittest.mock import patch
    from infrastructure.event_bus.event_bus import EventBus
    from infrastructure.windows.keyboard_controller import KeyboardController
    from application.interaction.action_executor import ActionExecutor
    from application.interaction.multimodal_coordinator import MultimodalCoordinator
    from modules.adaptation.interaction_outcome_tracker import InteractionOutcomeTracker
    from modules.multimodal.fusion_engine import FusionEngine

    for failure in (None, RuntimeError("Keyboard unavailable")):
        service, _, _, _ = create_service()
        service.event_bus = EventBus()
        tracker = InteractionOutcomeTracker()
        mouse = MagicMock()
        coordinator = MultimodalCoordinator(
            event_bus=service.event_bus,
            fusion_engine=FusionEngine(),
            action_executor=ActionExecutor(mouse, KeyboardController()),
            mouse_controller=mouse,
            interaction_outcome_tracker=tracker,
        )
        recognizer = MagicMock()
        recognizer.process_audio.return_value = "enter"
        with patch("application.interaction.multimodal_coordinator.threading.Timer"), \
             patch("infrastructure.windows.keyboard_controller.pyautogui.press", side_effect=failure) as press:
            try:
                assert service.process_audio(b"audio", recognizer) == "enter"
                coordinator._flush()
                press.assert_called_once_with("enter")
                outcome = tracker.snapshot()
                assert outcome["action_attempts"] == 1
                assert outcome["action_successes"] == (1 if failure is None else 0)
                assert outcome["action_failures"] == (0 if failure is None else 1)
            finally:
                coordinator.stop()
