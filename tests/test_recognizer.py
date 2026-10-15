import json

from unittest.mock import (
    MagicMock,
    patch
)

from modules.voice.recognizer import (
    VoiceRecognizer
)


@patch(
    "modules.voice.recognizer."
    "Path.exists",
    return_value=True
)
@patch(
    "modules.voice.recognizer.Model"
)
@patch(
    "modules.voice.recognizer."
    "KaldiRecognizer"
)
def test_grammar_contains_activate_dictation(
    mock_kaldi,
    mock_model,
    mock_exists
):

    VoiceRecognizer()

    args = mock_kaldi.call_args.args

    grammar = json.loads(
        args[2]
    )

    assert (
        "activar dictado"
        in grammar
    )

    assert "[unk]" in grammar


@patch(
    "modules.voice.recognizer."
    "Path.exists",
    return_value=True
)
@patch(
    "modules.voice.recognizer.Model"
)
@patch(
    "modules.voice.recognizer."
    "KaldiRecognizer"
)
def test_activate_dictation_is_recognized(
    mock_kaldi,
    mock_model,
    mock_exists
):

    fake_recognizer = MagicMock()

    mock_kaldi.return_value = (
        fake_recognizer
    )

    fake_recognizer.AcceptWaveform \
        .return_value = True

    fake_recognizer.Result \
        .return_value = json.dumps({
            "text": "activar dictado",
            "result": [
                {
                    "word": "activar",
                    "conf": 0.95
                },
                {
                    "word": "dictado",
                    "conf": 0.95
                }
            ]
        })

    recognizer = VoiceRecognizer()

    result = recognizer.process_audio(
        b"audio"
    )

    assert result == "activar dictado"


@patch(
    "modules.voice.recognizer."
    "Path.exists",
    return_value=True
)
@patch(
    "modules.voice.recognizer.Model"
)
@patch(
    "modules.voice.recognizer."
    "KaldiRecognizer"
)
def test_unknown_phrase_is_rejected(
    mock_kaldi,
    mock_model,
    mock_exists
):

    fake_recognizer = MagicMock()

    mock_kaldi.return_value = (
        fake_recognizer
    )

    fake_recognizer.AcceptWaveform \
        .return_value = True

    fake_recognizer.Result \
        .return_value = json.dumps({
            "text": "frase desconocida",
            "result": [
                {
                    "word": "frase",
                    "conf": 0.99
                },
                {
                    "word": "desconocida",
                    "conf": 0.99
                }
            ]
        })

    recognizer = VoiceRecognizer()

    result = recognizer.process_audio(
        b"audio"
    )

    assert result is None

    assert (
        recognizer.last_status
        == VoiceRecognizer.STATUS_UNKNOWN
    )

def test_reset_recognizer():

    recognizer = VoiceRecognizer.__new__(
        VoiceRecognizer
    )

    recognizer.recognizer = MagicMock()

    recognizer.reset()

    recognizer.recognizer.Reset \
        .assert_called_once()

@patch(
    "modules.voice.recognizer."
    "Path.exists",
    return_value=True
)
@patch(
    "modules.voice.recognizer.Model"
)
@patch(
    "modules.voice.recognizer."
    "KaldiRecognizer"
)
def test_partial_audio_is_not_an_error(
    mock_kaldi,
    mock_model,
    mock_exists
):

    fake_recognizer = MagicMock()

    mock_kaldi.return_value = (
        fake_recognizer
    )

    fake_recognizer.AcceptWaveform \
        .return_value = False

    recognizer = (
        VoiceRecognizer()
    )

    result = (
        recognizer.process_audio(
            b"audio"
        )
    )

    assert result is None

    assert (
        recognizer.last_status
        == VoiceRecognizer.STATUS_PARTIAL
    )