from unittest.mock import patch

from infrastructure.windows.mouse_controller import (
    MouseController
)


def test_right_click():

    mouse = MouseController()

    with patch(
        "infrastructure.windows.mouse_controller.pyautogui.click"
    ) as mock_click:

        mouse.right_click()

        mock_click.assert_called_once_with(
            button="right"
        )


def test_double_click():

    mouse = MouseController()

    with patch(
        "infrastructure.windows.mouse_controller.pyautogui.doubleClick"
    ) as mock_double_click:

        mouse.double_click()

        mock_double_click.assert_called_once_with(
            button="left",
            interval=0.15
        )


def test_start_drag():

    mouse = MouseController()

    with patch(
        "infrastructure.windows.mouse_controller.pyautogui.mouseDown"
    ) as mock_mouse_down:

        mouse.start_drag()

        mock_mouse_down.assert_called_once_with(
            button="left"
        )

        assert mouse.is_dragging() is True


def test_stop_drag():

    mouse = MouseController()

    with patch(
        "infrastructure.windows.mouse_controller.pyautogui.mouseDown"
    ), patch(
        "infrastructure.windows.mouse_controller.pyautogui.mouseUp"
    ) as mock_mouse_up:

        mouse.start_drag()

        assert mouse.is_dragging() is True

        mouse.stop_drag()

        mock_mouse_up.assert_called_once_with(
            button="left"
        )

        assert mouse.is_dragging() is False


def test_start_drag_only_once():

    mouse = MouseController()

    with patch(
        "infrastructure.windows.mouse_controller.pyautogui.mouseDown"
    ) as mock_mouse_down:

        mouse.start_drag()
        mouse.start_drag()

        assert mock_mouse_down.call_count == 1


def test_stop_drag_without_drag_does_nothing():

    mouse = MouseController()

    with patch(
        "infrastructure.windows.mouse_controller.pyautogui.mouseUp"
    ) as mock_mouse_up:

        mouse.stop_drag()

        mock_mouse_up.assert_not_called()