from unittest.mock import MagicMock

from application.interaction.dictation_service import (
    DictationService
)

from modules.voice.voice_mode import (
    VoiceModeManager
)


def create_service():

    recognizer = MagicMock()

    text_controller = MagicMock()

    mode_manager = VoiceModeManager()

    service = DictationService(
        recognizer=recognizer,
        text_input_controller=text_controller,
        voice_mode_manager=mode_manager
    )

    return (
        service,
        recognizer,
        text_controller,
        mode_manager
    )


def test_start_activates_dictation():

    (
        service,
        recognizer,
        _,
        mode_manager
    ) = create_service()

    result = service.start()

    assert result is True

    assert (
        mode_manager
        .is_dictation_mode()
    )

    recognizer.reset \
        .assert_called_once()


def test_stop_returns_to_command_mode():

    (
        service,
        recognizer,
        _,
        mode_manager
    ) = create_service()

    service.start()

    recognizer.reset.reset_mock()

    result = service.stop()

    assert result is True

    assert (
        mode_manager
        .is_command_mode()
    )

    recognizer.reset \
        .assert_called_once()


def test_audio_is_ignored_when_not_dictating():

    (
        service,
        recognizer,
        text_controller,
        _
    ) = create_service()

    result = service.process_audio(
        b"audio"
    )

    assert result is None

    recognizer.process_audio \
        .assert_not_called()

    text_controller.write_text \
        .assert_not_called()


def test_recognized_text_is_written():

    (
        service,
        recognizer,
        text_controller,
        _
    ) = create_service()

    service.start()

    recognizer.process_audio \
        .return_value = (
            "hola mundo"
        )

    result = service.process_audio(
        b"audio"
    )

    assert result == "hola mundo"

    text_controller.write_text \
        .assert_called_once_with(
            "hola mundo"
        )


def test_none_result_is_not_written():

    (
        service,
        recognizer,
        text_controller,
        _
    ) = create_service()

    service.start()

    recognizer.process_audio \
        .return_value = None

    result = service.process_audio(
        b"audio"
    )

    assert result is None

    text_controller.write_text \
        .assert_not_called()


def test_exit_phrase_stops_dictation():

    (
        service,
        recognizer,
        text_controller,
        mode_manager
    ) = create_service()

    service.start()

    recognizer.process_audio \
        .return_value = (
            "zero ui finalizar dictado"
        )

    result = service.process_audio(
        b"audio"
    )

    assert (
        result
        == DictationService.EXIT_PHRASE
    )

    assert (
        mode_manager
        .is_command_mode()
    )

    text_controller.write_text \
        .assert_not_called()


def test_exit_phrase_is_case_insensitive():

    (
        service,
        recognizer,
        text_controller,
        mode_manager
    ) = create_service()

    service.start()

    recognizer.process_audio \
        .return_value = (
            "ZERO UI FINALIZAR DICTADO"
        )

    service.process_audio(
        b"audio"
    )

    assert (
        mode_manager
        .is_command_mode()
    )

    text_controller.write_text \
        .assert_not_called()

def test_deactivate_dictation_phrase():

    (
        service,
        recognizer,
        text_controller,
        mode_manager
    ) = create_service()

    service.start()

    recognizer.process_audio \
        .return_value = (
            "desactivar dictado"
        )

    result = service.process_audio(
        b"audio"
    )

    assert (
        result
        == DictationService.EXIT_PHRASE
    )

    assert (
        mode_manager
        .is_command_mode()
    )

    text_controller.write_text \
        .assert_not_called()

def test_finish_dictation_alternative_phrase():

    (
        service,
        recognizer,
        text_controller,
        mode_manager
    ) = create_service()

    service.start()

    recognizer.process_audio \
        .return_value = (
            "finalizar dictado"
        )

    service.process_audio(
        b"audio"
    )

    assert (
        mode_manager
        .is_command_mode()
    )

    text_controller.write_text \
        .assert_not_called()