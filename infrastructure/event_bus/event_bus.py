from collections import defaultdict
from threading import RLock

from domain.events.interaction_event import (
    InteractionEvent
)

from domain.events.event_types import (
    EventType
)


class EventBus:
    """
    Canal interno de comunicación entre
    los diferentes componentes de ZeroUI-AC.

    Permite publicar eventos y que otros
    componentes se suscriban sin depender
    directamente entre sí.
    """

    def __init__(self):

        self._subscribers = defaultdict(list)

        self._global_subscribers = []

        self._lock = RLock()

    def subscribe(
        self,
        event_type: EventType,
        callback
    ):
        """
        Suscribe una función a un tipo
        específico de evento.
        """

        with self._lock:

            if (
                callback
                not in self._subscribers[event_type]
            ):

                self._subscribers[
                    event_type
                ].append(callback)

    def subscribe_all(self, callback):
        """
        Suscribe una función a todos
        los eventos.
        """

        with self._lock:

            if (
                callback
                not in self._global_subscribers
            ):

                self._global_subscribers.append(
                    callback
                )

    def unsubscribe(
        self,
        event_type: EventType,
        callback
    ):
        """
        Elimina una suscripción.
        """

        with self._lock:

            subscribers = (
                self._subscribers[event_type]
            )

            if callback in subscribers:
                subscribers.remove(callback)

    def unsubscribe_all(self, callback):
        """
        Elimina una suscripción global.
        """

        with self._lock:

            if (
                callback
                in self._global_subscribers
            ):

                self._global_subscribers.remove(
                    callback
                )

    def publish(
        self,
        event: InteractionEvent
    ):
        """
        Publica un evento a todos
        los suscriptores correspondientes.
        """

        with self._lock:

            callbacks = list(
                self._subscribers[
                    event.event_type
                ]
            )

            global_callbacks = list(
                self._global_subscribers
            )

        for callback in callbacks:
            callback(event)

        for callback in global_callbacks:
            callback(event)