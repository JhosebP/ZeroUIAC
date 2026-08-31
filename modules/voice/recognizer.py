import json
from pathlib import Path

from vosk import Model, KaldiRecognizer

from modules.voice.voice_commands import (
    VOICE_COMMANDS
)


class VoiceRecognizer:

    def __init__(
        self,
        model_path="resources/models/vosk-es",
        sample_rate=16000
    ):

        self.model_path = Path(
            model_path
        )

        self.sample_rate = sample_rate

        if not self.model_path.exists():

            raise FileNotFoundError(
                "No se encontró el modelo Vosk en: "
                f"{self.model_path}"
            )

        self.model = Model(
            str(self.model_path)
        )

        grammar = VOICE_COMMANDS.copy()

        grammar.append(
            "[unk]"
        )

        self.recognizer = KaldiRecognizer(
            self.model,
            self.sample_rate,
            json.dumps(
                grammar,
                ensure_ascii=False
            )
        )

    def process_audio(self, audio_data):

        if audio_data is None:
            return None

        if not self.recognizer.AcceptWaveform(
            audio_data
        ):
            return None

        result = json.loads(
            self.recognizer.Result()
        )

        text = result.get(
            "text",
            ""
        ).strip()

        if text in VOICE_COMMANDS:
            return text

        return None