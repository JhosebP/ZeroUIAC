from domain.events.event_types import (
    EventSource,
    EventType
)


class PriorityResolver:
    """
    Resuelve conflictos cuando diferentes
    canales producen eventos que compiten
    por la misma acción.

    Esta prioridad es inicial y determinista.

    En el Sprint 4 podrá ser ajustada
    dinámicamente por el sistema adaptativo.
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

    def _score(self, event):
        """
        Calcula la prioridad efectiva
        de un evento.
        """

        return (
            event.priority,
            self.TYPE_PRIORITY.get(
                event.event_type,
                0
            ),
            self.SOURCE_PRIORITY.get(
                event.source,
                0
            ),
            event.confidence,
            -event.timestamp
        )

    def resolve(self, events):
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

            key = event.get_conflict_key()

            if key not in groups:
                groups[key] = []

            groups[key].append(event)

        resolved = []

        for group_events in groups.values():

            winner = max(
                group_events,
                key=self._score
            )

            resolved.append(winner)

        resolved.sort(
            key=lambda event:
                event.timestamp
        )

        return resolved