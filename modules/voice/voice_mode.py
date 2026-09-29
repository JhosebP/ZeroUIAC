from enum import Enum
from threading import RLock


class VoiceMode(str, Enum):
    """
    Modos de funcionamiento del sistema de voz.
    """

    COMMAND = "command"
    DICTATION = "dictation"


class VoiceModeManager:
    """
    Gestiona el modo actual del sistema de voz.

    COMMAND:
        El audio se interpreta como comandos
        de ZeroUI-AC.

    DICTATION:
        El audio se interpreta como texto
        libre para escribir en la aplicación
        activa.
    """

    def __init__(self):

        self._mode = VoiceMode.COMMAND

        self._lock = RLock()

    @property
    def mode(self):
        """
        Devuelve el modo actual.
        """

        with self._lock:
            return self._mode

    def is_command_mode(self):
        """
        Indica si el sistema está
        en modo comandos.
        """

        with self._lock:

            return (
                self._mode
                == VoiceMode.COMMAND
            )

    def is_dictation_mode(self):
        """
        Indica si el sistema está
        en modo dictado.
        """

        with self._lock:

            return (
                self._mode
                == VoiceMode.DICTATION
            )

    def activate_dictation(self):
        """
        Cambia del modo comandos
        al modo dictado.
        """

        with self._lock:

            self._mode = (
                VoiceMode.DICTATION
            )

    def deactivate_dictation(self):
        """
        Finaliza el dictado y vuelve
        al modo comandos.
        """

        with self._lock:

            self._mode = (
                VoiceMode.COMMAND
            )