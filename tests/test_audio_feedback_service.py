from unittest.mock import patch

from infrastructure.windows.audio_feedback_service import (
    AudioFeedbackService
)


def test_audio_enabled_by_default():

    service = (
        AudioFeedbackService()
    )

    assert (
        service.enabled
        is True
    )


def test_audio_can_be_disabled():

    service = (
        AudioFeedbackService()
    )

    service.disable()

    assert (
        service.enabled
        is False
    )


def test_audio_can_be_enabled():

    service = (
        AudioFeedbackService(
            enabled=False
        )
    )

    service.enable()

    assert (
        service.enabled
        is True
    )


def test_set_enabled_changes_state():

    service = (
        AudioFeedbackService()
    )

    service.set_enabled(
        False
    )

    assert (
        service.enabled
        is False
    )


@patch(
    "infrastructure.windows."
    "audio_feedback_service."
    "winsound.Beep"
)
def test_success_sound_is_played(
    mock_beep
):

    service = (
        AudioFeedbackService(
            frequency=880,
            duration_ms=80
        )
    )

    result = (
        service.play_success()
    )

    mock_beep.assert_called_once_with(
        880,
        80
    )

    assert result is True


@patch(
    "infrastructure.windows."
    "audio_feedback_service."
    "winsound.Beep"
)
def test_disabled_audio_does_not_play(
    mock_beep
):

    service = (
        AudioFeedbackService(
            enabled=False
        )
    )

    result = (
        service.play_success()
    )

    mock_beep.assert_not_called()

    assert result is False