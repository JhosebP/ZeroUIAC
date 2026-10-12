from unittest.mock import MagicMock

from application.interaction.multimodal_coordinator import (
    MultimodalCoordinator
)

from domain.commands.system_actions import (
    SystemAction
)

from domain.events.event_types import (
    EventSource,
    EventType
)

from domain.events.interaction_event import (
    InteractionEvent
)


def create_coordinator():

    event_bus = MagicMock()
    fusion_engine = MagicMock()
    action_executor = MagicMock()
    mouse = MagicMock()

    coordinator = MultimodalCoordinator(
        event_bus=event_bus,
        fusion_engine=fusion_engine,
        action_executor=action_executor,
        mouse_controller=mouse
    )

    return (
        coordinator,
        event_bus,
        fusion_engine,
        action_executor,
        mouse
    )


def test_subscribes_to_event_bus():

    (
        coordinator,
        event_bus,
        _,
        _,
        _
    ) = create_coordinator()

    event_bus.subscribe_all \
        .assert_called_once_with(
            coordinator._receive_event
        )


def test_execute_action_event():

    (
        coordinator,
        _,
        _,
        action_executor,
        _
    ) = create_coordinator()

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY
    )

    coordinator._execute_event(
        event
    )

    action_executor.execute \
        .assert_called_once_with(
            SystemAction.COPY
        )


def test_execute_relative_cursor():

    (
        coordinator,
        _,
        _,
        _,
        mouse
    ) = create_coordinator()

    event = InteractionEvent(
        source=EventSource.HEAD,
        event_type=EventType.CURSOR_MOVE,
        payload={
            "mode": "relative",
            "dx": 5,
            "dy": -3
        }
    )

    coordinator._execute_event(
        event
    )

    mouse.move_relative \
        .assert_called_once_with(
            5,
            -3
        )


def test_execute_absolute_cursor():

    (
        coordinator,
        _,
        _,
        _,
        mouse
    ) = create_coordinator()

    event = InteractionEvent(
        source=EventSource.LIMB,
        event_type=EventType.CURSOR_MOVE,
        payload={
            "mode": "absolute",
            "x": 500,
            "y": 300
        }
    )

    coordinator._execute_event(
        event
    )

    mouse.move_to \
        .assert_called_once_with(
            500,
            300
        )

def test_draw_action_controls_overlay():

    (
        coordinator,
        _,
        _,
        action_executor,
        _
    ) = create_coordinator()

    overlay = MagicMock()

    coordinator.overlay_service = (
        overlay
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.DRAW
    )

    coordinator._execute_event(
        event
    )

    overlay.toggle_draw \
        .assert_called_once()

    action_executor.execute \
        .assert_not_called()


def test_erase_action_controls_overlay():

    (
        coordinator,
        _,
        _,
        action_executor,
        _
    ) = create_coordinator()

    overlay = MagicMock()

    coordinator.overlay_service = (
        overlay
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.ERASE
    )

    coordinator._execute_event(
        event
    )

    overlay.toggle_erase \
        .assert_called_once()

    action_executor.execute \
        .assert_not_called()

def test_zoom_in_action_controls_zoom_service():

    (
        coordinator,
        _,
        _,
        action_executor,
        _
    ) = create_coordinator()

    zoom_service = (
        MagicMock()
    )

    coordinator.zoom_service = (
        zoom_service
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.ZOOM_IN
    )

    coordinator._execute_event(
        event
    )

    zoom_service.zoom_in \
        .assert_called_once()

    action_executor.execute \
        .assert_not_called()


def test_zoom_out_action_controls_zoom_service():

    (
        coordinator,
        _,
        _,
        action_executor,
        _
    ) = create_coordinator()

    zoom_service = (
        MagicMock()
    )

    coordinator.zoom_service = (
        zoom_service
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.ZOOM_OUT
    )

    coordinator._execute_event(
        event
    )

    zoom_service.zoom_out \
        .assert_called_once()

    action_executor.execute \
        .assert_not_called()

def test_normal_action_shows_feedback():

    event_bus = MagicMock()

    fusion_engine = MagicMock()

    action_executor = MagicMock()

    mouse = MagicMock()

    overlay = MagicMock()

    coordinator = (
        MultimodalCoordinator(
            event_bus=event_bus,
            fusion_engine=(
                fusion_engine
            ),
            action_executor=(
                action_executor
            ),
            mouse_controller=mouse,
            overlay_service=overlay
        )
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY
    )

    coordinator._execute_event(
        event
    )

    action_executor.execute \
        .assert_called_once_with(
            SystemAction.COPY
        )

    overlay.show_feedback \
        .assert_called_once_with(
            "Copiar"
        )


def test_zoom_shows_visual_feedback():

    event_bus = MagicMock()

    fusion_engine = MagicMock()

    action_executor = MagicMock()

    mouse = MagicMock()

    overlay = MagicMock()

    zoom_service = MagicMock()

    zoom_service.zoom_in \
        .return_value = True

    zoom_service.current_zoom = (
        1.25
    )

    coordinator = (
        MultimodalCoordinator(
            event_bus=event_bus,
            fusion_engine=(
                fusion_engine
            ),
            action_executor=(
                action_executor
            ),
            mouse_controller=mouse,
            overlay_service=overlay,
            zoom_service=(
                zoom_service
            )
        )
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.ZOOM_IN
    )

    coordinator._execute_event(
        event
    )

    overlay.show_feedback \
        .assert_called_once_with(
            "Zoom 125%"
        )

def test_normal_action_plays_audio_feedback():

    event_bus = MagicMock()

    fusion_engine = MagicMock()

    action_executor = MagicMock()

    mouse = MagicMock()

    overlay = MagicMock()

    audio_feedback = MagicMock()

    coordinator = (
        MultimodalCoordinator(
            event_bus=event_bus,
            fusion_engine=(
                fusion_engine
            ),
            action_executor=(
                action_executor
            ),
            mouse_controller=mouse,
            overlay_service=overlay,
            audio_feedback_service=(
                audio_feedback
            )
        )
    )

    event = InteractionEvent(
        source=EventSource.VOICE,
        event_type=EventType.ACTION,
        action=SystemAction.COPY
    )

    coordinator._execute_event(
        event
    )

    audio_feedback \
        .play_success \
        .assert_called_once()


def test_cursor_movement_does_not_play_audio():

    event_bus = MagicMock()

    fusion_engine = MagicMock()

    action_executor = MagicMock()

    mouse = MagicMock()

    audio_feedback = MagicMock()

    coordinator = (
        MultimodalCoordinator(
            event_bus=event_bus,
            fusion_engine=(
                fusion_engine
            ),
            action_executor=(
                action_executor
            ),
            mouse_controller=mouse,
            audio_feedback_service=(
                audio_feedback
            )
        )
    )

    event = InteractionEvent(
        source=EventSource.HEAD,
        event_type=EventType.CURSOR_MOVE,
        payload={
            "mode": "relative",
            "dx": 5,
            "dy": 3
        }
    )

    coordinator._execute_event(
        event
    )

    audio_feedback \
        .play_success \
        .assert_not_called()