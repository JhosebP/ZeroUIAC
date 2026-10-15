import threading

from domain.events.event_types import (
    EventSource,
    EventType
)

from domain.events.interaction_event import (
    InteractionEvent
)

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

from application.interaction.zoom_mode_manager import (
    ZoomModeManager
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

    ACTIVATE_ZOOM_COMMAND = (
        "activar zoom"
    )

    DEACTIVATE_ZOOM_COMMAND = (
        "desactivar zoom"
    )

    def __init__(
        self,
        event_bus,
        calibration_profile,
        dictation_service,
        voice_mode_manager,
        zoom_mode_manager=None
    ):
        self.event_bus = (
            event_bus
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

        if zoom_mode_manager is None:

            zoom_mode_manager = (
                ZoomModeManager()
            )

        self.zoom_mode_manager = (
            zoom_mode_manager
        )

        self.stop_event = (
            threading.Event()
        )

        self.thread = None

    def _publish_voice_error(
        self,
        message,
        reason
    ):
        """
        Publica un evento de estado
        correspondiente a un error
        de reconocimiento de voz.
        """

        event = InteractionEvent(
            source=EventSource.VOICE,
            event_type=EventType.STATUS,
            payload={
                "level": "error",
                "message": message,
                "reason": reason
            }
        )

        self.event_bus.publish(
            event
        )

    def _publish_voice_feedback(
        self,
        message,
        reason
    ):
        """
        Publica una confirmación de estado
        producida por un comando de voz.
        """

        event = InteractionEvent(
            source=EventSource.VOICE,
            event_type=EventType.STATUS,
            payload={
                "level": "success",
                "message": message,
                "reason": reason
            }
        )

        self.event_bus.publish(
            event
        )

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
            .process_audio(
                audio
            )
        )

        if command is None:

            status = getattr(
                recognizer,
                "last_status",
                None
            )

            # Con MagicMock y otros
            # reconocedores de prueba,
            # evitamos interpretar objetos
            # arbitrarios como estados.
            if not isinstance(
                status,
                str
            ):
                return None

            if (
                status
                == VoiceRecognizer
                .STATUS_UNKNOWN
            ):

                self._publish_voice_error(
                    message=(
                        "Comando no reconocido"
                    ),
                    reason=(
                        "unknown_command"
                    )
                )

            elif (
                status
                == VoiceRecognizer
                .STATUS_LOW_CONFIDENCE
            ):

                self._publish_voice_error(
                    message=(
                        "No se pudo confirmar "
                        "el comando"
                    ),
                    reason=(
                        "low_confidence"
                    )
                )

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

        if (
            command
            == self.ACTIVATE_ZOOM_COMMAND
        ):
        
            self.zoom_mode_manager.enable()
        
            self._publish_voice_feedback(
                message="Modo zoom activado",
                reason="zoom_mode_enabled"
            )
        
            print(
                "Modo zoom activado."
            )
        
            return command
        
        
        if (
            command
            == self.DEACTIVATE_ZOOM_COMMAND
        ):
        
            self.zoom_mode_manager.disable()
        
            self._publish_voice_feedback(
                message="Modo zoom desactivado",
                reason="zoom_mode_disabled"
            )
        
            print(
                "Modo zoom desactivado."
            )
        
            return command

        action = (
            VOICE_ACTION_MAP
            .get(command)
        )

        if action is None:

            self._publish_voice_error(
                message=(
                    "Comando sin acción disponible"
                ),
                reason=(
                    "action_not_available"
                )
            )

            return command

        event = InteractionEvent(
            source=EventSource.VOICE,
            event_type=EventType.ACTION,
            action=action,
            confidence=1.0,
            conflict_key="action"
        )

        self.event_bus.publish(
            event
        )

        print(
            f"Evento de voz publicado: "
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
            .process_audio(
                audio
            )
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
            f"Texto dictado: "
            f"{result}"
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

            print(
                error
            )

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

                audio = (
                    microphone.read()
                )

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

        self.thread = (
            threading.Thread(
                target=self._run,
                daemon=True
            )
        )

        self.thread.start()

    def stop(self):

        self.stop_event.set()

        if self.thread is not None:

            self.thread.join(
                timeout=2
            )