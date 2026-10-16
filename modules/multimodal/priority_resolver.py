from domain.events.event_types import (
    EventSource,
    EventType
)


class PriorityResolver:
    """
    Resuelve conflictos cuando diferentes
    canales producen eventos que compiten
    por la misma acción.

    La prioridad base permanece
    determinista.

    Los pesos adaptativos solamente
    modifican la prioridad relativa
    del canal.
    """

    SOURCE_PRIORITY = {

        EventSource.SYSTEM: 100,

        EventSource.VOICE: 80,

        EventSource.GESTURE: 70,

        EventSource.LIMB: 60,

        EventSource.HEAD: 50,
    }

    TYPE_PRIORITY = {

        EventType.ACTION: 100,

        EventType.GESTURE: 80,

        EventType.CURSOR_MOVE: 50,

        EventType.STATUS: 10,
    }

    SYSTEM_SOURCE_SCORE = 100.0

    MAX_ADAPTIVE_SOURCE_SCORE = 99.0

    def __init__(
        self,
        channel_weights=None
    ):

        self.channel_weights = (
            channel_weights
        )

    def _get_source_weight(
        self,
        source
    ):
        """
        Obtiene el peso adaptativo.

        Si no existe componente adaptativo
        o éste falla, utiliza peso neutral.
        """

        if source == EventSource.SYSTEM:
            return 1.0

        if self.channel_weights is None:
            return 1.0

        try:

            weight = float(
                self.channel_weights
                .get_weight(source)
            )

            if weight <= 0.0:
                return 1.0

            return weight

        except Exception:

            # Una falla adaptativa nunca
            # debe detener la fusión.
            return 1.0

    def _source_score(
        self,
        event
    ):
        """
        Calcula la prioridad efectiva
        del canal.

        SYSTEM mantiene siempre una
        autoridad superior a cualquier
        canal adaptativo.
        """

        base_priority = float(
            self.SOURCE_PRIORITY.get(
                event.source,
                0
            )
        )

        if (
            event.source
            == EventSource.SYSTEM
        ):

            return (
                self.SYSTEM_SOURCE_SCORE
            )

        weight = (
            self._get_source_weight(
                event.source
            )
        )

        effective_priority = (
            base_priority
            * weight
        )

        return min(
            effective_priority,
            self.MAX_ADAPTIVE_SOURCE_SCORE
        )

    def _score(
        self,
        event
    ):
        """
        Calcula la prioridad efectiva
        de un evento.

        Orden:

        1. prioridad manual
        2. tipo de evento
        3. peso/prioridad del canal
        4. confianza
        5. antigüedad
        """

        return (
            event.priority,

            self.TYPE_PRIORITY.get(
                event.event_type,
                0
            ),

            self._source_score(
                event
            ),

            event.confidence,

            -event.timestamp
        )

    def resolve(
        self,
        events
    ):
        """
        Recibe una colección de eventos.

        Los eventos pertenecientes al mismo
        grupo de conflicto compiten entre sí.

        Los eventos de grupos diferentes
        pueden continuar simultáneamente.
        """

        if not events:
            return []

        groups = {}

        for event in events:

            key = (
                event.get_conflict_key()
            )

            if key not in groups:
                groups[key] = []

            groups[key].append(
                event
            )

        resolved = []

        for group_events in (
            groups.values()
        ):

            winner = max(
                group_events,
                key=self._score
            )

            resolved.append(
                winner
            )

        resolved.sort(
            key=lambda event:
            event.timestamp
        )

        return resolved