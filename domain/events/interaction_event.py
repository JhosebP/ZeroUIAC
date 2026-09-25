from dataclasses import dataclass, field
from time import monotonic
from typing import Any

from domain.commands.system_actions import (
    SystemAction
)

from domain.events.event_types import (
    EventSource,
    EventType
)


@dataclass(frozen=True)
class InteractionEvent:
    """
    Representa un evento de interacción
    producido dentro de ZeroUI-AC.

    El evento puede provenir de:
    - voz
    - cabeza
    - extremidad
    - gesto
    - sistema
    """

    source: EventSource

    event_type: EventType

    action: SystemAction | None = None

    payload: dict[str, Any] = field(
        default_factory=dict
    )

    confidence: float = 1.0

    priority: int = 0

    conflict_key: str | None = None

    timestamp: float = field(
        default_factory=monotonic
    )

    def __post_init__(self):
        """
        Valida que el evento tenga
        información coherente.
        """

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "La confianza debe estar "
                "entre 0.0 y 1.0."
            )

        if (
            self.event_type == EventType.ACTION
            and self.action is None
        ):
            raise ValueError(
                "Un evento ACTION debe "
                "contener una SystemAction."
            )

    def get_conflict_key(self):
        """
        Obtiene el grupo de conflicto
        utilizado por PriorityResolver.
        """

        if self.conflict_key:
            return self.conflict_key

        if self.event_type == EventType.ACTION:
            return "action"

        if self.event_type == EventType.CURSOR_MOVE:
            return "cursor"

        if self.event_type == EventType.GESTURE:
            return "gesture"

        return (
            f"status:"
            f"{self.source.value}:"
            f"{self.timestamp}"
        )