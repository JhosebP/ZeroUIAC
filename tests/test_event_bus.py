from domain.commands.system_actions import SystemAction

from domain.events.event_types import (
    EventSource,
    EventType
)

from domain.events.interaction_event import (
    InteractionEvent
)

from infrastructure.event_bus.event_bus import (
    EventBus
)


def create_action_event():
    return InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY,
        confidence=0.95
    )


def test_subscriber_receives_event():

    bus = EventBus()

    received = []

    def callback(event):
        received.append(event)

    bus.subscribe(
        EventType.ACTION,
        callback
    )

    event = create_action_event()

    bus.publish(event)

    assert len(received) == 1
    assert received[0] == event


def test_global_subscriber_receives_event():

    bus = EventBus()

    received = []

    def callback(event):
        received.append(event)

    bus.subscribe_all(callback)

    event = create_action_event()

    bus.publish(event)

    assert len(received) == 1
    assert received[0] == event


def test_wrong_event_type_is_not_received():

    bus = EventBus()

    received = []

    def callback(event):
        received.append(event)

    bus.subscribe(
        EventType.CURSOR_MOVE,
        callback
    )

    event = create_action_event()

    bus.publish(event)

    assert len(received) == 0


def test_unsubscribe():

    bus = EventBus()

    received = []

    def callback(event):
        received.append(event)

    bus.subscribe(
        EventType.ACTION,
        callback
    )

    bus.unsubscribe(
        EventType.ACTION,
        callback
    )

    bus.publish(
        create_action_event()
    )

    assert len(received) == 0


def test_unsubscribe_all():

    bus = EventBus()

    received = []

    def callback(event):
        received.append(event)

    bus.subscribe_all(callback)

    bus.unsubscribe_all(callback)

    bus.publish(
        create_action_event()
    )

    assert len(received) == 0