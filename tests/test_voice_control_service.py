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

    event_bus.publish \
        .assert_not_called()


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


def test_pending_sprint3_command_is_not_published():

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
        .assert_not_called()