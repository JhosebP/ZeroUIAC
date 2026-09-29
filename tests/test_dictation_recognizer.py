from unittest.mock import (
    MagicMock,
    patch
)

from modules.voice.dictation_recognizer import (
    DictationRecognizer
)



@patch(
    "modules.voice."
    "dictation_recognizer."
    "os.path.exists",
    return_value=True
)
@patch(
    "modules.voice."
    "dictation_recognizer."
    "Model"
)
@patch(
    "modules.voice."
    "dictation_recognizer."
    "KaldiRecognizer"
)
def test_recognizer_is_created_without_closed_grammar(
    mock_kaldi,
    mock_model,
    mock_exists
):

    recognizer = DictationRecognizer()

    mock_model.assert_called_once()

    mock_kaldi.assert_called_once_with(
        mock_model.return_value,
        16000
    )

    recognizer.recognizer.SetWords \
        .assert_called_once_with(True)


@patch(
    "modules.voice."
    "dictation_recognizer."
    "os.path.exists",
    return_value=True
)
@patch(
    "modules.voice."
    "dictation_recognizer."
    "Model"
)
@patch(
    "modules.voice."
    "dictation_recognizer."
    "KaldiRecognizer"
)
def test_returns_final_text(
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
        .return_value = (
            '{"text": "hola mundo"}'
        )

    recognizer = DictationRecognizer()

    result = recognizer.process_audio(
        b"audio"
    )

    assert result == "hola mundo"


@patch(
    "modules.voice."
    "dictation_recognizer."
    "os.path.exists",
    return_value=True
)
@patch(
    "modules.voice."
    "dictation_recognizer."
    "Model"
)
@patch(
    "modules.voice."
    "dictation_recognizer."
    "KaldiRecognizer"
)
def test_partial_audio_returns_none(
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

    recognizer = DictationRecognizer()

    result = recognizer.process_audio(
        b"audio"
    )

    assert result is None


@patch(
    "modules.voice."
    "dictation_recognizer."
    "os.path.exists",
    return_value=True
)
@patch(
    "modules.voice."
    "dictation_recognizer."
    "Model"
)
@patch(
    "modules.voice."
    "dictation_recognizer."
    "KaldiRecognizer"
)
def test_empty_result_returns_none(
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
        .return_value = (
            '{"text": ""}'
        )

    recognizer = DictationRecognizer()

    result = recognizer.process_audio(
        b"audio"
    )

    assert result is None


@patch(
    "modules.voice."
    "dictation_recognizer."
    "os.path.exists",
    return_value=True
)
@patch(
    "modules.voice."
    "dictation_recognizer."
    "Model"
)
@patch(
    "modules.voice."
    "dictation_recognizer."
    "KaldiRecognizer"
)
def test_partial_text(
    mock_kaldi,
    mock_model,
    mock_exists
):

    fake_recognizer = MagicMock()

    mock_kaldi.return_value = (
        fake_recognizer
    )

    fake_recognizer.PartialResult \
        .return_value = (
            '{"partial": "buenos dias"}'
        )

    recognizer = DictationRecognizer()

    result = (
        recognizer.get_partial_text()
    )

    assert result == "buenos dias"


@patch(
    "modules.voice."
    "dictation_recognizer."
    "os.path.exists",
    return_value=False
)
def test_missing_model_raises_error(
    mock_exists
):

    try:

        DictationRecognizer()

        assert False

    except FileNotFoundError:

        assert True