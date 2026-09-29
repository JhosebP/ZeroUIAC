import json
from pathlib import Path

from vosk import (
    Model,
    KaldiRecognizer
)

from modules.voice.voice_commands import (
    VOICE_GRAMMAR
)


class VoiceRecognizer:
    """
    Reconocimiento offline de comandos
    de voz mediante Vosk.
    """

    def __init__(
        self,
        model_path="resources/models/vosk-es",
        sample_rate=16000,
        confidence_threshold=0.80
    ):
        self.model_path = Path(
            model_path
        )

        self.sample_rate = (
            sample_rate
        )

        self.confidence_threshold = (
            confidence_threshold
        )

        if not self.model_path.exists():

            raise FileNotFoundError(
                "No se encontró el modelo "
                "Vosk en: "
                f"{self.model_path}"
            )

        self.model = Model(
            str(self.model_path)
        )

        grammar = (
            VOICE_GRAMMAR.copy()
        )

        grammar.append(
            "[unk]"
        )

        self.recognizer = (
            KaldiRecognizer(
                self.model,
                self.sample_rate,
                json.dumps(
                    grammar,
                    ensure_ascii=False
                )
            )
        )

        self.recognizer.SetWords(
            True
        )

    def process_audio(
        self,
        audio_data
    ):

        if audio_data is None:
            return None

        if not (
            self.recognizer
            .AcceptWaveform(
                audio_data
            )
        ):
            return None

        result = json.loads(
            self.recognizer.Result()
        )

        text = (
            result
            .get("text", "")
            .strip()
        )

        if not text:
            return None

        # Aceptar solamente frases
        # pertenecientes a la gramática
        # de control de ZeroUI-AC.
        if text not in VOICE_GRAMMAR:
            return None

        words = result.get(
            "result",
            []
        )

        if not words:
            return None

        confidences = [
            word.get(
                "conf",
                0.0
            )
            for word in words
        ]

        confidence = (
            sum(confidences)
            / len(confidences)
        )

        if (
            confidence
            < self.confidence_threshold
        ):

            print(
                f"Comando descartado: "
                f"{text} "
                f"(confianza: "
                f"{confidence:.2f})"
            )

            return None

        print(
            f"Confianza: "
            f"{confidence:.2f}"
        )

        return text

    def reset(self):
        """
        Reinicia el estado interno
        del reconocedor de comandos.
        """

        self.recognizer.Reset()