from unittest.mock import Mock

import pytest

from infrastructure.windows import text_input_controller as text_input
from infrastructure.windows.text_input_controller import TextInputController


@pytest.fixture
def clipboard(monkeypatch):
    state = {"text": "previous code", "order": [], "inserted": [], "pending": False}

    def copy(text):
        state["order"].append(("copy", text))
        state["text"] = text

    def hotkey(*keys):
        state["order"].append(("paste", keys))
        state["pending"] = True

    def sleep(delay):
        state["order"].append(("wait", delay))
        # Model a destination consuming the clipboard after Ctrl+V returns.
        if state["pending"]:
            state["inserted"].append(state["text"])
            state["pending"] = False

    monkeypatch.setattr(text_input.pyperclip, "paste", lambda: state["text"])
    monkeypatch.setattr(text_input.pyperclip, "copy", Mock(side_effect=copy))
    monkeypatch.setattr(text_input.pyautogui, "hotkey", Mock(side_effect=hotkey))
    monkeypatch.setattr(text_input.time, "sleep", Mock(side_effect=sleep))
    return state


def test_write_text(clipboard):
    assert TextInputController().write_text("hola mundo") is True
    assert clipboard["inserted"] == ["hola mundo "]
    assert clipboard["text"] == "previous code"


def test_write_text_without_space(clipboard):
    assert TextInputController().write_text("hola", add_space=False) is True
    assert clipboard["inserted"] == ["hola"]
    assert clipboard["text"] == "previous code"


def test_clipboard_paste_wait_restore_order_is_configurable(clipboard):
    assert TextInputController(paste_delay=0.45).write_text("hola") is True
    assert clipboard["order"] == [
        ("copy", "hola "),
        ("paste", ("ctrl", "v")),
        ("wait", 0.45),
        ("copy", "previous code"),
    ]


def test_default_paste_delay_is_300_ms():
    assert TextInputController().paste_delay == 0.30


@pytest.mark.parametrize("value", [None, "", "   ", "\n\t"])
def test_empty_text_is_ignored(clipboard, value):
    assert TextInputController().write_text(value) is False
    assert clipboard["order"] == []
    assert clipboard["text"] == "previous code"


def test_unicode_text(clipboard):
    text = "\u00e1 \u00e9 \u00ed \u00f3 \u00fa \u00f1 \u00bf \u00a1"
    assert TextInputController().write_text(text) is True
    assert clipboard["inserted"] == [text + " "]
    assert clipboard["text"] == "previous code"


def test_paste_failure_returns_false_and_waits_before_restoring(clipboard):
    original_hotkey = text_input.pyautogui.hotkey.side_effect

    def partial_hotkey(*keys):
        original_hotkey(*keys)
        raise RuntimeError("Hotkey failed after dispatch")

    text_input.pyautogui.hotkey.side_effect = partial_hotkey
    assert TextInputController().write_text("hola") is False
    assert clipboard["order"] == [
        ("copy", "hola "), ("paste", ("ctrl", "v")),
        ("wait", 0.30), ("copy", "previous code"),
    ]
    assert clipboard["text"] == "previous code"


def test_backup_failure_does_not_change_clipboard(clipboard, monkeypatch):
    monkeypatch.setattr(text_input.pyperclip, "paste", Mock(side_effect=RuntimeError))
    assert TextInputController().write_text("hola") is False
    text_input.pyperclip.copy.assert_not_called()
    text_input.pyautogui.hotkey.assert_not_called()


def test_copy_failure_restores_if_text_was_already_written(clipboard):
    original_copy = text_input.pyperclip.copy.side_effect

    def partial_copy(text):
        original_copy(text)
        if text == "hola ":
            raise RuntimeError("Copy partially completed")

    text_input.pyperclip.copy.side_effect = partial_copy
    assert TextInputController().write_text("hola") is False
    assert clipboard["text"] == "previous code"
    text_input.pyautogui.hotkey.assert_not_called()


def test_unverified_copy_is_not_pasted(clipboard):
    text_input.pyperclip.copy.side_effect = None
    assert TextInputController().write_text("hola") is False
    assert clipboard["text"] == "previous code"
    text_input.pyautogui.hotkey.assert_not_called()


def test_restore_failure_returns_false(clipboard):
    original_copy = text_input.pyperclip.copy.side_effect

    def copy(text):
        if text == "previous code":
            raise RuntimeError("Clipboard unavailable")
        original_copy(text)

    text_input.pyperclip.copy.side_effect = copy
    assert TextInputController().write_text("hola") is False
    assert clipboard["inserted"] == ["hola "]


def test_wait_failure_still_restores_clipboard(clipboard):
    text_input.time.sleep.side_effect = RuntimeError("Wait failed")
    assert TextInputController().write_text("hola") is False
    assert clipboard["text"] == "previous code"


def test_external_clipboard_change_is_preserved(clipboard):
    original_sleep = text_input.time.sleep.side_effect

    def sleep(delay):
        original_sleep(delay)
        clipboard["text"] = "new external copy"

    text_input.time.sleep.side_effect = sleep
    assert TextInputController().write_text("hola") is True
    assert clipboard["text"] == "new external copy"
    assert clipboard["inserted"] == ["hola "]


def test_consecutive_phrases_do_not_paste_previous_clipboard(clipboard):
    controller = TextInputController()
    assert controller.write_text("primera frase") is True
    assert controller.write_text("segunda frase") is True
    assert clipboard["inserted"] == ["primera frase ", "segunda frase "]
    assert "".join(clipboard["inserted"]) == "primera frase segunda frase "
    assert clipboard["text"] == "previous code"


def test_zero_delay_is_supported_for_explicit_configuration(clipboard):
    assert TextInputController(paste_delay=0).write_text("hola") is True
    text_input.time.sleep.assert_not_called()
    assert clipboard["text"] == "previous code"


@pytest.mark.parametrize("delay", [-1, float("nan"), float("inf")])
def test_invalid_delay_is_rejected(delay):
    with pytest.raises(ValueError):
        TextInputController(paste_delay=delay)
