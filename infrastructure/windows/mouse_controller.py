import ctypes
import pyautogui


class MouseController:

    SAFE_MARGIN = 8

    def _clamp_point(
        self,
        x,
        y
    ):
        """
        Evita colocar el cursor exactamente
        en las esquinas de la pantalla.
        """

        width, height = (
            pyautogui.size()
        )

        margin = self.SAFE_MARGIN

        min_x = margin
        min_y = margin

        max_x = max(
            margin,
            width - 1 - margin
        )

        max_y = max(
            margin,
            height - 1 - margin
        )

        safe_x = max(
            min_x,
            min(max_x, int(x))
        )

        safe_y = max(
            min_y,
            min(max_y, int(y))
        )

        return safe_x, safe_y

    def _recover_cursor_from_corner(
        self
    ):
        """
        Recupera el cursor cuando el
        FailSafe de PyAutoGUI detecta
        una esquina.

        Se mantiene FAILSAFE activado.
        """

        try:

            x, y = (
                pyautogui.position()
            )

            safe_x, safe_y = (
                self._clamp_point(
                    x,
                    y
                )
            )

            ctypes.windll \
                .user32 \
                .SetCursorPos(
                    safe_x,
                    safe_y
                )

        except Exception:
            pass

    """
    Controla las acciones del mouse de Windows
    mediante PyAutoGUI.
    """

    def __init__(self):
        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = True

        self.dragging = False

    def move_relative(
        self,
        dx,
        dy
    ):
        """
        Movimiento relativo protegido
        contra las esquinas de pantalla.
        """

        current_x, current_y = (
            pyautogui.position()
        )

        target_x = (
            current_x + dx
        )

        target_y = (
            current_y + dy
        )

        target_x, target_y = (
            self._clamp_point(
                target_x,
                target_y
            )
        )

        try:

            pyautogui.moveTo(
                target_x,
                target_y,
                duration=0
            )

            return True

        except pyautogui.FailSafeException:

            self._recover_cursor_from_corner()

            return False

    def move_to(
        self,
        x,
        y
    ):
        """
        Movimiento absoluto protegido
        contra las esquinas de pantalla.
        """

        target_x, target_y = (
            self._clamp_point(
                x,
                y
            )
        )

        try:

            pyautogui.moveTo(
                target_x,
                target_y,
                duration=0
            )

            return True

        except pyautogui.FailSafeException:

            self._recover_cursor_from_corner()

            return False

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
        Devuelve la posición actual
        del cursor en pantalla.
        """

        position = (
            pyautogui.position()
        )

        return (
            position.x,
            position.y
        )

    def get_screen_size(self):
        """
        Obtiene las dimensiones de la pantalla.
        """

        return pyautogui.size()