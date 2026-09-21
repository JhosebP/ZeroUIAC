import pyautogui


class KeyboardController:
    """
    Emula acciones y combinaciones estándar
    del teclado de Windows mediante PyAutoGUI.
    """

    def __init__(self):
        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = True

    def copy(self):
        pyautogui.hotkey(
            "ctrl",
            "c"
        )

    def paste(self):
        pyautogui.hotkey(
            "ctrl",
            "v"
        )

    def cut(self):
        pyautogui.hotkey(
            "ctrl",
            "x"
        )

    def undo(self):
        pyautogui.hotkey(
            "ctrl",
            "z"
        )

    def save(self):
        pyautogui.hotkey(
            "ctrl",
            "s"
        )

    def select_all(self):
        pyautogui.hotkey(
            "ctrl",
            "a"
        )

    def switch_app(self):
        """
        Abre la Vista de tareas de Windows.
        """

        pyautogui.hotkey(
            "win",
            "tab"
        )

    def navigate_up(self):
        pyautogui.press(
            "up"
        )

    def navigate_down(self):
        pyautogui.press(
            "down"
        )

    def navigate_left(self):
        pyautogui.press(
            "left"
        )

    def navigate_right(self):
        pyautogui.press(
            "right"
        )