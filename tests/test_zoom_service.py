from unittest.mock import (
    MagicMock
)

from application.interaction.zoom_service import (
    ZoomService
)


def create_service():

    magnification = (
        MagicMock()
    )

    magnification.set_zoom \
        .return_value = True

    magnification.reset \
        .return_value = True

    mouse = MagicMock()

    mouse.get_position \
        .return_value = (
            960,
            540
        )

    mouse.get_screen_size \
        .return_value = (
            1920,
            1080
        )

    service = ZoomService(
        magnification_controller=(
            magnification
        ),
        mouse_controller=(
            mouse
        )
    )

    return (
        service,
        magnification,
        mouse
    )


def test_default_zoom_is_100_percent():

    service, _, _ = (
        create_service()
    )

    assert (
        service.current_zoom
        == 1.0
    )


def test_zoom_in_increases_25_percent():

    service, _, _ = (
        create_service()
    )

    result = (
        service.zoom_in()
    )

    assert result is True

    assert (
        service.current_zoom
        == 1.25
    )


def test_zoom_out_decreases_25_percent():

    service, _, _ = (
        create_service()
    )

    service.current_zoom = (
        2.0
    )

    service.zoom_out()

    assert (
        service.current_zoom
        == 1.75
    )


def test_zoom_cannot_exceed_400_percent():

    service, _, _ = (
        create_service()
    )

    service.current_zoom = (
        4.0
    )

    result = (
        service.zoom_in()
    )

    assert result is False

    assert (
        service.current_zoom
        == 4.0
    )


def test_zoom_cannot_go_below_100_percent():

    service, _, _ = (
        create_service()
    )

    result = (
        service.zoom_out()
    )

    assert result is False

    assert (
        service.current_zoom
        == 1.0
    )


def test_zoom_uses_cursor_as_focus():

    (
        service,
        magnification,
        _
    ) = create_service()

    service.zoom_in()

    magnification.set_zoom \
        .assert_called_once_with(
            level=1.25,
            focus_x=960,
            focus_y=540,
            screen_width=1920,
            screen_height=1080
        )


def test_reset_returns_to_100_percent():

    (
        service,
        magnification,
        _
    ) = create_service()

    service.current_zoom = (
        2.5
    )

    service.reset()

    assert (
        service.current_zoom
        == 1.0
    )

    magnification.reset \
        .assert_called_once()