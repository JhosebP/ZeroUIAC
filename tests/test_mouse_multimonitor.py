from unittest.mock import (
    patch
)

from infrastructure.windows.mouse_controller import (
    MouseController
)



def test_virtual_screen_size():

    mouse = (
        MouseController()
    )

    with patch.object(
        mouse,
        "get_virtual_screen_bounds",
        return_value=(
            -1920,
            0,
            3840,
            1080
        )
    ):

        width, height = (
            mouse.get_screen_size()
        )

        assert width == 3840
        assert height == 1080


def test_virtual_screen_allows_negative_coordinates():

    mouse = (
        MouseController()
    )

    with patch.object(
        mouse,
        "get_virtual_screen_bounds",
        return_value=(
            -1920,
            0,
            3840,
            1080
        )
    ):

        x, y = (
            mouse._clamp_point(
                -1000,
                500
            )
        )

        assert x == -1000
        assert y == 500


def test_virtual_screen_protects_outer_edges():

    mouse = (
        MouseController()
    )

    with patch.object(
        mouse,
        "get_virtual_screen_bounds",
        return_value=(
            -1920,
            0,
            3840,
            1080
        )
    ):

        x, y = (
            mouse._clamp_point(
                -5000,
                -5000
            )
        )

        assert x == -1912
        assert y == 8