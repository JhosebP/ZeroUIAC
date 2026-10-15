import ctypes
import pyautogui


class MouseController:

    SAFE_MARGIN = 8

    SM_XVIRTUALSCREEN = 76
    SM_YVIRTUALSCREEN = 77
    SM_CXVIRTUALSCREEN = 78
    SM_CYVIRTUALSCREEN = 79

    def get_virtual_screen_bounds(
        self
    ):
        """
        Devuelve el rectángulo completo
        del escritorio virtual de Windows.
    
        Puede incluir coordenadas negativas
        cuando existe un monitor a la izquierda
        o encima de la pantalla principal.
        """
    
        user32 = (
            ctypes.windll.user32
        )
    
        left = (
            user32.GetSystemMetrics(
                self.SM_XVIRTUALSCREEN
            )
        )
    
        top = (
            user32.GetSystemMetrics(
                self.SM_YVIRTUALSCREEN
            )
        )
    
        width = (
            user32.GetSystemMetrics(
                self.SM_CXVIRTUALSCREEN
            )
        )
    
        height = (
            user32.GetSystemMetrics(
                self.SM_CYVIRTUALSCREEN
            )
        )
    
        return (
            left,
            top,
            width,
            height
        )

    def _clamp_point(
        self,
        x,
        y
    ):
        """
        Mantiene el cursor dentro del
        escritorio virtual completo y evita
        sus esquinas extremas.
        """

        (
            left,
            top,
            width,
            height
        ) = (
            self.get_virtual_screen_bounds()
        )

        margin = (
            self.SAFE_MARGIN
        )

        min_x = (
            left + margin
        )

        min_y = (
            top + margin
        )

        max_x = max(
            min_x,
            left
            + width
            - 1
            - margin
        )

        max_y = max(
            min_y,
            top
            + height
            - 1
            - margin
        )

        safe_x = max(
            min_x,
            min(
                max_x,
                int(x)
            )
        )

        safe_y = max(
            min_y,
            min(
                max_y,
                int(y)
            )
        )

        return (
            safe_x,
            safe_y
        )

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
        Obtiene las dimensiones totales
        del escritorio virtual.
        """
    
        (
            _,
            _,
            width,
            height
        ) = (
            self.get_virtual_screen_bounds()
        )
    
        return (
            width,
            height
        )