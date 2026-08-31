import pyautogui


class MouseController:
    """
    Controla el mouse de Windows mediante PyAutoGUI.
    """

    def __init__(self):

        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = True

    def move_relative(self, dx, dy):

        if dx == 0 and dy == 0:
            return

        pyautogui.moveRel(
            dx,
            dy,
            duration=0
        )

    def move_to(self, x, y):

        pyautogui.moveTo(
            x,
            y,
            duration=0
        )

    def left_click(self):

        pyautogui.click(
            button="left"
        )

    def get_position(self):

        return pyautogui.position()

    def get_screen_size(self):

        return pyautogui.size()