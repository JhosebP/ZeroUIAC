import threading

from modules.voice.microphone import (
    MicrophoneStream
)

from modules.voice.recognizer import (
    VoiceRecognizer
)


class VoiceControlService:
    """
    Gestiona el reconocimiento de voz
    en un hilo independiente.
    """

    def __init__(
        self,
        mouse_controller,
        calibration_profile
    ):

        self.mouse_controller = mouse_controller

        self.profile = calibration_profile

        self.stop_event = threading.Event()

        self.thread = None

    def _run(self):
        """
        Proceso interno de reconocimiento de voz.
        """

        recognizer = VoiceRecognizer(
            sample_rate=(
                self.profile.microphone_sample_rate
            )
        )

        microphone = MicrophoneStream(
            sample_rate=(
                self.profile.microphone_sample_rate
            ),
            gain=(
                self.profile.microphone_gain
            )
        )

        microphone.start()

        print(
            "Reconocimiento de voz iniciado."
        )

        try:

            while not self.stop_event.is_set():

                audio = microphone.read()

                if audio is None:
                    continue

                command = recognizer.process_audio(
                    audio
                )

                if command is None:
                    continue

                print(
                    f"Comando reconocido: {command}"
                )

                # Durante el Sprint 1
                # implementamos clic izquierdo.
                if command == "clic":

                    self.mouse_controller.left_click()

        finally:

            microphone.stop()

    def start(self):
        """
        Inicia el reconocimiento de voz.
        """

        self.stop_event.clear()

        self.thread = threading.Thread(
            target=self._run,
            daemon=True
        )

        self.thread.start()

    def stop(self):
        """
        Detiene el reconocimiento de voz.
        """

        self.stop_event.set()

        if self.thread is not None:

            self.thread.join(
                timeout=2
            )