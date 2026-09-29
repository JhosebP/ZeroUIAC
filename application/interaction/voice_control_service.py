import threading

from modules.voice.microphone import (
    MicrophoneStream
)

from modules.voice.recognizer import (
    VoiceRecognizer
)

from modules.voice.voice_commands import (
    VOICE_ACTION_MAP
)

from application.interaction.dictation_service import (
    DictationService
)


class VoiceControlService:
    """
    Gestiona el canal de voz de ZeroUI-AC.

    El audio puede trabajar en dos modos:

    COMMAND:
        Reconoce comandos predefinidos.

    DICTATION:
        Reconoce texto libre y lo escribe
        en la aplicación activa.
    """

    ACTIVATE_DICTATION_COMMAND = (
        "activar dictado"
    )

    def __init__(
        self,
        action_executor,
        calibration_profile,
        dictation_service,
        voice_mode_manager
    ):
        self.action_executor = (
            action_executor
        )

        self.profile = (
            calibration_profile
        )

        self.dictation_service = (
            dictation_service
        )

        self.voice_mode_manager = (
            voice_mode_manager
        )

        self.stop_event = (
            threading.Event()
        )

        self.thread = None

    def _process_command_mode(
        self,
        audio,
        recognizer
    ):
        """
        Procesa audio cuando el sistema
        está en modo COMMAND.
        """

        command = (
            recognizer
            .process_audio(audio)
        )

        if command is None:
            return None

        print(
            f"Comando reconocido: "
            f"{command}"
        )

        if (
            command
            == self.ACTIVATE_DICTATION_COMMAND
        ):
            recognizer.reset()

            self.dictation_service.start()

            print(
                "Modo dictado activado."
            )

            return (
                self.ACTIVATE_DICTATION_COMMAND
            )

        action = (
            VOICE_ACTION_MAP
            .get(command)
        )

        if action is None:

            print(
                "Comando reconocido, "
                "pero su función se "
                "implementará en "
                "Sprint 3."
            )

            return command

        executed = (
            self.action_executor
            .execute(action)
        )

        if executed:

            print(
                f"Acción ejecutada: "
                f"{action.value}"
            )

        return command

    def _process_dictation_mode(
        self,
        audio,
        recognizer
    ):
        """
        Procesa audio cuando el sistema
        está en modo DICTATION.
        """

        result = (
            self.dictation_service
            .process_audio(audio)
        )

        if result is None:
            return None

        if (
            result
            == DictationService.EXIT_PHRASE
        ):
            recognizer.reset()

            print(
                "Modo dictado finalizado."
            )

            print(
                "Modo comandos activado."
            )

            return result

        print(
            f"Texto dictado: {result}"
        )

        return result

    def process_audio(
        self,
        audio,
        recognizer
    ):
        """
        Decide qué reconocedor debe procesar
        el audio según el modo actual.
        """

        if (
            self.voice_mode_manager
            .is_dictation_mode()
        ):

            return (
                self._process_dictation_mode(
                    audio,
                    recognizer
                )
            )

        return (
            self._process_command_mode(
                audio,
                recognizer
            )
        )

    def _run(self):

        try:

            recognizer = VoiceRecognizer(
                sample_rate=(
                    self.profile
                    .microphone_sample_rate
                )
            )

        except FileNotFoundError as error:

            print("")
            print(
                "ERROR DE VOZ:"
            )
            print(error)

            return

        microphone = MicrophoneStream(
            sample_rate=(
                self.profile
                .microphone_sample_rate
            ),
            gain=(
                self.profile
                .microphone_gain
            )
        )

        try:

            microphone.start()

            print(
                "Reconocimiento de voz iniciado."
            )

            while (
                not self.stop_event.is_set()
            ):

                audio = microphone.read()

                if audio is None:
                    continue

                self.process_audio(
                    audio,
                    recognizer
                )

        finally:

            microphone.stop()

    def start(self):

        self.stop_event.clear()

        self.thread = threading.Thread(
            target=self._run,
            daemon=True
        )

        self.thread.start()

    def stop(self):

        self.stop_event.set()

        if self.thread is not None:

            self.thread.join(
                timeout=2
            )