import json
import os

from vosk import (
    KaldiRecognizer,
    Model
)


class DictationRecognizer:
    """
    Reconocedor de voz destinado al
    modo de dictado libre de ZeroUI-AC.

    A diferencia del reconocedor de comandos,
    este componente NO utiliza una gramática
    cerrada.

    Por lo tanto, puede reconocer frases
    completas en español.
    """

    DEFAULT_MODEL_PATH = os.path.join(
        "resources",
        "models",
        "vosk-es"
    )

    def __init__(
        self,
        model_path=None,
        sample_rate=16000
    ):

        self.model_path = (
            model_path
            or self.DEFAULT_MODEL_PATH
        )

        self.sample_rate = sample_rate

        if not os.path.exists(
            self.model_path
        ):
            raise FileNotFoundError(
                "No se encontró el modelo "
                f"de Vosk en: "
                f"{self.model_path}"
            )

        self.model = Model(
            self.model_path
        )

        self.recognizer = (
            KaldiRecognizer(
                self.model,
                self.sample_rate
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
        Procesa un bloque de audio.

        Retorna texto únicamente cuando
        Vosk determina que existe un
        resultado final.

        Si todavía está procesando audio,
        retorna None.
        """

        if audio_data is None:
            return None

        if not audio_data:
            return None

        accepted = (
            self.recognizer.AcceptWaveform(
                audio_data
            )
        )

        if not accepted:
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

        return text

    def get_partial_text(self):
        """
        Obtiene el texto parcial reconocido.

        Este método será útil posteriormente
        para mostrar retroalimentación visual
        mientras el usuario habla.
        """

        result = json.loads(
            self.recognizer.PartialResult()
        )

        text = (
            result
            .get("partial", "")
            .strip()
        )

        if not text:
            return None

        return text

    def reset(self):
        """
        Reinicia el estado interno
        del reconocedor.
        """

        self.recognizer.Reset()