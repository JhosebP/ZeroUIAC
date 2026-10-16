from modules.multimodal.priority_resolver import (
    PriorityResolver
)

from modules.multimodal.channel_manager import (
    ChannelManager
)


class FusionEngine:
    """
    Motor inicial de fusión multimodal
    de ZeroUI-AC.

    Recibe eventos procedentes de los
    diferentes canales y determina cuáles
    deben continuar hacia la ejecución.
    """

    def __init__(
        self,
        priority_resolver=None,
        channel_manager=None,
        channel_weights=None
    ):
    
        if priority_resolver is None:
    
            priority_resolver = (
                PriorityResolver(
                    channel_weights=(
                        channel_weights
                    )
                )
            )
    
        self.priority_resolver = (
            priority_resolver
        )
    
        self.channel_manager = (
            channel_manager
            or ChannelManager()
        )

    def process_events(self, events):
        """
        Procesa uno o varios eventos
        detectados dentro de una misma
        ventana de interacción.
        """

        if not events:
            return []

        enabled_events = [

            event

            for event in events

            if self.channel_manager.is_enabled(
                event.source
            )
        ]

        if not enabled_events:
            return []

        return (
            self.priority_resolver
            .resolve(enabled_events)
        )

    def process_event(self, event):
        """
        Método auxiliar para procesar
        solamente un evento.
        """

        return self.process_events(
            [event]
        )