from unittest.mock import patch

from infrastructure.windows.text_input_controller import (
    TextInputController
)


def test_write_text():

    controller = TextInputController(
        paste_delay=0
    )

    with patch(
        "infrastructure.windows."
        "text_input_controller."
        "pyperclip.paste",
        return_value="contenido anterior"
    ), patch(
        "infrastructure.windows."
        "text_input_controller."
        "pyperclip.copy"
    ) as mock_copy, patch(
        "infrastructure.windows."
        "text_input_controller."
        "pyautogui.hotkey"
    ) as mock_hotkey:

        result = controller.write_text(
            "hola mundo"
        )

        assert result is True

        assert (
            mock_copy.call_count
            == 2
        )

        mock_copy.assert_any_call(
            "hola mundo "
        )

        mock_copy.assert_any_call(
            "contenido anterior"
        )

        mock_hotkey.assert_called_once_with(
            "ctrl",
            "v"
        )


def test_write_text_without_space():

    controller = TextInputController(
        paste_delay=0
    )

    with patch(
        "infrastructure.windows."
        "text_input_controller."
        "pyperclip.paste",
        return_value=""
    ), patch(
        "infrastructure.windows."
        "text_input_controller."
        "pyperclip.copy"
    ) as mock_copy, patch(
        "infrastructure.windows."
        "text_input_controller."
        "pyautogui.hotkey"
    ):

        result = controller.write_text(
            "hola",
            add_space=False
        )

        assert result is True

        mock_copy.assert_any_call(
            "hola"
        )


def test_empty_text_is_ignored():

    controller = TextInputController(
        paste_delay=0
    )

    with patch(
        "infrastructure.windows."
        "text_input_controller."
        "pyautogui.hotkey"
    ) as mock_hotkey:

        result = controller.write_text(
            ""
        )

        assert result is False

        mock_hotkey.assert_not_called()


def test_none_is_ignored():

    controller = TextInputController(
        paste_delay=0
    )

    with patch(
        "infrastructure.windows."
        "text_input_controller."
        "pyautogui.hotkey"
    ) as mock_hotkey:

        result = controller.write_text(
            None
        )

        assert result is False

        mock_hotkey.assert_not_called()


def test_unicode_text():

    controller = TextInputController(
        paste_delay=0
    )

    with patch(
        "infrastructure.windows."
        "text_input_controller."
        "pyperclip.paste",
        return_value=""
    ), patch(
        "infrastructure.windows."
        "text_input_controller."
        "pyperclip.copy"
    ) as mock_copy, patch(
        "infrastructure.windows."
        "text_input_controller."
        "pyautogui.hotkey"
    ):

        result = controller.write_text(
            "aplicación española"
        )

        assert result is True

        mock_copy.assert_any_call(
            "aplicación española "
        )