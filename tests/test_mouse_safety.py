import pyautogui

from unittest.mock import (
    patch
)

from infrastructure.windows.mouse_controller import (
    MouseController
)


def test_absolute_movement_avoids_corner():

    mouse = MouseController()

    with (
        patch(
            "infrastructure.windows."
            "mouse_controller.pyautogui.size",
            return_value=(1920, 1080)
        ),
        patch(
            "infrastructure.windows."
            "mouse_controller.pyautogui.moveTo"
        ) as move_to
    ):

        result = mouse.move_to(
            0,
            0
        )

        assert result is True

        move_to.assert_called_once_with(
            8,
            8,
            duration=0
        )


def test_relative_movement_avoids_corner():

    mouse = MouseController()

    with (
        patch(
            "infrastructure.windows."
            "mouse_controller.pyautogui.size",
            return_value=(1920, 1080)
        ),
        patch(
            "infrastructure.windows."
            "mouse_controller.pyautogui.position",
            return_value=(10, 10)
        ),
        patch(
            "infrastructure.windows."
            "mouse_controller.pyautogui.moveTo"
        ) as move_to
    ):

        result = mouse.move_relative(
            -100,
            -100
        )

        assert result is True

        move_to.assert_called_once_with(
            8,
            8,
            duration=0
        )


def test_failsafe_is_caught():

    mouse = MouseController()

    with (
        patch(
            "infrastructure.windows."
            "mouse_controller.pyautogui.size",
            return_value=(1920, 1080)
        ),
        patch(
            "infrastructure.windows."
            "mouse_controller.pyautogui.moveTo",
            side_effect=(
                pyautogui
                .FailSafeException()
            )
        ),
        patch.object(
            mouse,
            "_recover_cursor_from_corner"
        ) as recover
    ):

        result = mouse.move_to(
            500,
            500
        )

        assert result is False

        recover.assert_called_once()