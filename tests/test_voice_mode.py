from modules.voice.voice_mode import (
    VoiceMode,
    VoiceModeManager
)


def test_default_mode_is_command():

    manager = VoiceModeManager()

    assert (
        manager.mode
        == VoiceMode.COMMAND
    )


def test_command_mode_by_default():

    manager = VoiceModeManager()

    assert (
        manager.is_command_mode()
        is True
    )

    assert (
        manager.is_dictation_mode()
        is False
    )


def test_activate_dictation():

    manager = VoiceModeManager()

    manager.activate_dictation()

    assert (
        manager.mode
        == VoiceMode.DICTATION
    )

    assert (
        manager.is_dictation_mode()
        is True
    )


def test_deactivate_dictation():

    manager = VoiceModeManager()

    manager.activate_dictation()

    manager.deactivate_dictation()

    assert (
        manager.mode
        == VoiceMode.COMMAND
    )

    assert (
        manager.is_command_mode()
        is True
    )


def test_can_change_mode_multiple_times():

    manager = VoiceModeManager()

    manager.activate_dictation()

    assert manager.is_dictation_mode()

    manager.deactivate_dictation()

    assert manager.is_command_mode()

    manager.activate_dictation()

    assert manager.is_dictation_mode()