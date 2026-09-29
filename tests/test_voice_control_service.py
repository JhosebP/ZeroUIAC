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

from modules.voice.voice_mode import (
    VoiceModeManager
)


def create_service():

    action_executor = MagicMock()

    profile = SimpleNamespace(
        microphone_sample_rate=16000,
        microphone_gain=1.0
    )

    mode_manager = VoiceModeManager()

    dictation_service = MagicMock()

    service = VoiceControlService(
        action_executor=action_executor,
        calibration_profile=profile,
        dictation_service=dictation_service,
        voice_mode_manager=mode_manager
    )

    return (
        service,
        action_executor,
        dictation_service,
        mode_manager
    )


def test_normal_command_is_executed():

    (
        service,
        action_executor,
        _,
        _
    ) = create_service()

    recognizer = MagicMock()

    recognizer.process_audio.return_value = (
        "copiar"
    )

    action_executor.execute.return_value = (
        True
    )

    result = service.process_audio(
        b"audio",
        recognizer
    )

    assert result == "copiar"

    action_executor.execute \
        .assert_called_once_with(
            SystemAction.COPY
        )


def test_activate_dictation_starts_service():

    (
        service,
        action_executor,
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

    action_executor.execute \
        .assert_not_called()


def test_dictation_mode_routes_audio_to_dictation():

    (
        service,
        action_executor,
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

    action_executor.execute \
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


def test_pending_sprint3_command_is_not_executed():

    (
        service,
        action_executor,
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

    action_executor.execute \
        .assert_not_called()