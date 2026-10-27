import pyautogui

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

def test_left_click_releases_active_drag(
    monkeypatch
):

    events = []

    monkeypatch.setattr(
        pyautogui,
        "mouseDown",
        lambda button:
            events.append(
                ("down", button)
            )
    )

    monkeypatch.setattr(
        pyautogui,
        "mouseUp",
        lambda button:
            events.append(
                ("up", button)
            )
    )

    monkeypatch.setattr(
        pyautogui,
        "click",
        lambda button:
            events.append(
                ("click", button)
            )
    )

    mouse = MouseController()

    assert (
        mouse.start_drag()
        is True
    )

    assert (
        mouse.is_dragging()
        is True
    )

    mouse.left_click()

    assert (
        mouse.is_dragging()
        is False
    )

    assert events == [
        ("down", "left"),
        ("up", "left"),
        ("click", "left"),
    ]


def test_double_click_releases_active_drag(
    monkeypatch
):

    events = []

    monkeypatch.setattr(
        pyautogui,
        "mouseDown",
        lambda button:
            events.append(
                ("down", button)
            )
    )

    monkeypatch.setattr(
        pyautogui,
        "mouseUp",
        lambda button:
            events.append(
                ("up", button)
            )
    )

    monkeypatch.setattr(
        pyautogui,
        "doubleClick",
        lambda button, interval:
            events.append(
                ("double", button)
            )
    )

    mouse = MouseController()

    mouse.start_drag()

    mouse.double_click()

    assert (
        mouse.is_dragging()
        is False
    )

    assert events == [
        ("down", "left"),
        ("up", "left"),
        ("double", "left"),
    ]


def test_drag_can_start_again_after_click(
    monkeypatch
):

    downs = []

    monkeypatch.setattr(
        pyautogui,
        "mouseDown",
        lambda button:
            downs.append(button)
    )

    monkeypatch.setattr(
        pyautogui,
        "mouseUp",
        lambda button:
            None
    )

    monkeypatch.setattr(
        pyautogui,
        "click",
        lambda button:
            None
    )

    mouse = MouseController()

    assert (
        mouse.start_drag()
        is True
    )

    mouse.left_click()

    assert (
        mouse.start_drag()
        is True
    )

    assert downs == [
        "left",
        "left",
    ]


def test_repeated_start_drag_returns_false(
    monkeypatch
):

    monkeypatch.setattr(
        pyautogui,
        "mouseDown",
        lambda button:
            None
    )

    mouse = MouseController()

    assert (
        mouse.start_drag()
        is True
    )

    assert (
        mouse.start_drag()
        is False
    )