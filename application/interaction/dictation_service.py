import unicodedata
class DictationService:
    """
    Coordina el modo de dictado de ZeroUI-AC.

    Recibe audio ya capturado, obtiene el
    texto reconocido y lo envía a la
    aplicación activa de Windows.
    """

    EXIT_PHRASE = "desactivar dictado"

    EXIT_PHRASES = {
        "desactivar dictado",
        "finalizar dictado",
        "terminar dictado",
        "zero ui finalizar dictado",
        "cero ui finalizar dictado",
    }

    def __init__(
        self,
        recognizer,
        text_input_controller,
        voice_mode_manager
    ):
        self.recognizer = recognizer

        self.text_input_controller = (
            text_input_controller
        )

        self.voice_mode_manager = (
            voice_mode_manager
        )

    def start(self):
        """
        Activa el modo dictado.
        """

        self.recognizer.reset()

        self.voice_mode_manager \
            .activate_dictation()

        return True

    def stop(self):
        """
        Finaliza el modo dictado y vuelve
        al modo comandos.
        """

        self.recognizer.reset()

        self.voice_mode_manager \
            .deactivate_dictation()

        return True

    @staticmethod
    def _normalize_text(text):
        """
        Normaliza el texto reconocido para
        comparar comandos internos del dictado.
        """

        if text is None:
            return ""

        text = (
            str(text)
            .strip()
            .lower()
        )

        text = unicodedata.normalize(
            "NFD",
            text
        )

        text = "".join(
            character
            for character in text
            if unicodedata.category(character)
            != "Mn"
        )

        return " ".join(
            text.split()
        )

    def process_audio(
        self,
        audio_data
    ):
        """
        Procesa audio solamente cuando
        ZeroUI-AC está en modo dictado.

        Retorna:
        - None si aún no existe texto final.
        - El texto reconocido cuando se escribe.
        - EXIT_PHRASE cuando finaliza el dictado.
        """

        if not (
            self.voice_mode_manager
            .is_dictation_mode()
        ):
            return None

        text = (
            self.recognizer
            .process_audio(audio_data)
        )

        if text is None:
            return None

        normalized_text = (
            self._normalize_text(text)
        )

        if not normalized_text:
            return None

        if (
            normalized_text
            in self.EXIT_PHRASES
        ):
            self.stop()
        
            return self.EXIT_PHRASE

        self.text_input_controller \
            .write_text(text)

        return text