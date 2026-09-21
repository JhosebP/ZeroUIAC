from unittest.mock import patch

from infrastructure.windows.keyboard_controller import (
    KeyboardController
)


def test_copy():

    keyboard = KeyboardController()

    with patch(
        "infrastructure.windows."
        "keyboard_controller."
        "pyautogui.hotkey"
    ) as mock_hotkey:

        keyboard.copy()

        mock_hotkey.assert_called_once_with(
            "ctrl",
            "c"
        )


def test_paste():

    keyboard = KeyboardController()

    with patch(
        "infrastructure.windows."
        "keyboard_controller."
        "pyautogui.hotkey"
    ) as mock_hotkey:

        keyboard.paste()

        mock_hotkey.assert_called_once_with(
            "ctrl",
            "v"
        )


def test_switch_app():

    keyboard = KeyboardController()

    with patch(
        "infrastructure.windows."
        "keyboard_controller."
        "pyautogui.hotkey"
    ) as mock_hotkey:

        keyboard.switch_app()

        mock_hotkey.assert_called_once_with(
            "win",
            "tab"
        )


def test_navigation_up():

    keyboard = KeyboardController()

    with patch(
        "infrastructure.windows."
        "keyboard_controller."
        "pyautogui.press"
    ) as mock_press:

        keyboard.navigate_up()

        mock_press.assert_called_once_with(
            "up"
        )


def test_navigation_down():

    keyboard = KeyboardController()

    with patch(
        "infrastructure.windows."
        "keyboard_controller."
        "pyautogui.press"
    ) as mock_press:

        keyboard.navigate_down()

        mock_press.assert_called_once_with(
            "down"
        )


def test_navigation_left():

    keyboard = KeyboardController()

    with patch(
        "infrastructure.windows."
        "keyboard_controller."
        "pyautogui.press"
    ) as mock_press:

        keyboard.navigate_left()

        mock_press.assert_called_once_with(
            "left"
        )


def test_navigation_right():

    keyboard = KeyboardController()

    with patch(
        "infrastructure.windows."
        "keyboard_controller."
        "pyautogui.press"
    ) as mock_press:

        keyboard.navigate_right()

        mock_press.assert_called_once_with(
            "right"
        )