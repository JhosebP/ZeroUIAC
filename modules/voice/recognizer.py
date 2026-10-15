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

    STATUS_NO_AUDIO = "no_audio"
    STATUS_PARTIAL = "partial"
    STATUS_EMPTY = "empty"
    STATUS_UNKNOWN = "unknown"
    STATUS_LOW_CONFIDENCE = "low_confidence"
    STATUS_INVALID_RESULT = "invalid_result"
    STATUS_RECOGNIZED = "recognized"

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

        self.last_status = None
        self.last_text = None
        self.last_confidence = None

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
        """
        Procesa audio y conserva el estado
        del último resultado.

        Esto permite diferenciar:

        - silencio;
        - resultado parcial;
        - comando desconocido;
        - baja confianza;
        - comando reconocido.
        """

        self.last_status = None
        self.last_text = None
        self.last_confidence = None

        if audio_data is None:

            self.last_status = (
                self.STATUS_NO_AUDIO
            )

            return None

        if not (
            self.recognizer
            .AcceptWaveform(
                audio_data
            )
        ):

            self.last_status = (
                self.STATUS_PARTIAL
            )

            return None

        result = json.loads(
            self.recognizer.Result()
        )

        text = (
            result
            .get(
                "text",
                ""
            )
            .strip()
        )

        self.last_text = text

        if not text:

            self.last_status = (
                self.STATUS_EMPTY
            )

            return None

        if text not in VOICE_GRAMMAR:

            self.last_status = (
                self.STATUS_UNKNOWN
            )

            print(
                f"Comando no reconocido: "
                f"{text}"
            )

            return None

        words = (
            result.get(
                "result",
                []
            )
        )

        if not words:

            self.last_status = (
                self.STATUS_INVALID_RESULT
            )

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

        self.last_confidence = (
            confidence
        )

        if (
            confidence
            < self.confidence_threshold
        ):

            self.last_status = (
                self.STATUS_LOW_CONFIDENCE
            )

            print(
                f"Comando descartado: "
                f"{text} "
                f"(confianza: "
                f"{confidence:.2f})"
            )

            return None

        self.last_status = (
            self.STATUS_RECOGNIZED
        )

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

        self.last_status = None
        self.last_text = None
        self.last_confidence = None

        self.recognizer.Reset()