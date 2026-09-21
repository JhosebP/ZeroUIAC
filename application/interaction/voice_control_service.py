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


class VoiceControlService:
    """
    Gestiona el reconocimiento de voz offline
    y convierte los comandos reconocidos
    en acciones del sistema.
    """

    def __init__(
        self,
        action_executor,
        calibration_profile
    ):
        self.action_executor = (
            action_executor
        )

        self.profile = (
            calibration_profile
        )

        self.stop_event = (
            threading.Event()
        )

        self.thread = None

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

                command = (
                    recognizer
                    .process_audio(audio)
                )

                if command is None:
                    continue

                print(
                    f"Comando reconocido: "
                    f"{command}"
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

                    continue

                executed = (
                    self.action_executor
                    .execute(action)
                )

                if executed:

                    print(
                        f"Acción ejecutada: "
                        f"{action.value}"
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