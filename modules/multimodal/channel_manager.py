from domain.events.event_types import (
    EventSource
)


class ChannelManager:
    """
    Gestiona qué canales de interacción
    se encuentran habilitados.
    """

    def __init__(self):

        self._enabled_channels = {
            EventSource.VOICE: True,
            EventSource.HEAD: True,
            EventSource.LIMB: True,
            EventSource.GESTURE: True,
            EventSource.SYSTEM: True,
        }

    def enable(self, source: EventSource):
        """
        Habilita un canal.
        """

        self._enabled_channels[source] = True

    def disable(self, source: EventSource):
        """
        Deshabilita un canal.
        """

        self._enabled_channels[source] = False

    def set_enabled(
        self,
        source: EventSource,
        enabled: bool
    ):
        """
        Establece directamente el estado
        de un canal.
        """

        self._enabled_channels[source] = (
            bool(enabled)
        )

    def is_enabled(
        self,
        source: EventSource
    ):
        """
        Indica si un canal está habilitado.
        """

        return self._enabled_channels.get(
            source,
            False
        )

    def get_enabled_sources(self):
        """
        Devuelve los canales actualmente
        habilitados.
        """

        return [
            source
            for source, enabled
            in self._enabled_channels.items()
            if enabled
        ]