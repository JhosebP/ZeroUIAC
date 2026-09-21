import pyautogui


class MouseController:
    """
    Controla las acciones del mouse de Windows
    mediante PyAutoGUI.
    """

    def __init__(self):
        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = True

        self.dragging = False

    def move_relative(self, dx, dy):
        """
        Mueve el cursor de forma relativa.
        """

        if dx == 0 and dy == 0:
            return

        pyautogui.moveRel(
            dx,
            dy,
            duration=0
        )

    def move_to(self, x, y):
        """
        Mueve el cursor a una posición
        absoluta de la pantalla.
        """

        pyautogui.moveTo(
            x,
            y,
            duration=0
        )

    def left_click(self):
        """
        Ejecuta clic izquierdo.
        """

        pyautogui.click(
            button="left"
        )

    def right_click(self):
        """
        Ejecuta clic derecho.
        """

        pyautogui.click(
            button="right"
        )

    def double_click(self):
        """
        Ejecuta doble clic izquierdo.
        """

        pyautogui.doubleClick(
            button="left",
            interval=0.15
        )

    def start_drag(self):
        """
        Mantiene presionado el botón izquierdo
        para comenzar una operación de arrastre.
        """

        if self.dragging:
            return

        pyautogui.mouseDown(
            button="left"
        )

        self.dragging = True

    def stop_drag(self):
        """
        Libera el botón izquierdo y finaliza
        la operación de arrastre.
        """

        if not self.dragging:
            return

        pyautogui.mouseUp(
            button="left"
        )

        self.dragging = False

    def is_dragging(self):
        """
        Indica si actualmente existe
        una operación de arrastre.
        """

        return self.dragging

    def get_position(self):
        """
        Obtiene la posición actual del cursor.
        """

        return pyautogui.position()

    def get_screen_size(self):
        """
        Obtiene las dimensiones de la pantalla.
        """

        return pyautogui.size()