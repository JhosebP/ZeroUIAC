from domain.commands.system_actions import (
    SystemAction
)


class ActionExecutor:
    """
    Ejecuta las acciones internas de ZeroUI-AC
    utilizando los controladores correspondientes.

    De esta manera, voz y gestos no necesitan
    conocer directamente PyAutoGUI.
    """

    def __init__(
        self,
        mouse_controller,
        keyboard_controller
    ):
        self.mouse = mouse_controller
        self.keyboard = keyboard_controller

    def execute(self, action):
        """
        Ejecuta una acción del sistema.

        Retorna True si la acción fue reconocida
        y ejecutada.
        """

        if action == SystemAction.LEFT_CLICK:
            self.mouse.left_click()
            return True

        if action == SystemAction.RIGHT_CLICK:
            self.mouse.right_click()
            return True

        if action == SystemAction.DOUBLE_CLICK:
            self.mouse.double_click()
            return True

        if action == SystemAction.START_DRAG:
            self.mouse.start_drag()
            return True

        if action == SystemAction.STOP_DRAG:
            self.mouse.stop_drag()
            return True

        if action == SystemAction.COPY:
            self.keyboard.copy()
            return True

        if action == SystemAction.PASTE:
            self.keyboard.paste()
            return True

        if action == SystemAction.CUT:
            self.keyboard.cut()
            return True

        if action == SystemAction.UNDO:
            self.keyboard.undo()
            return True

        if action == SystemAction.SAVE:
            self.keyboard.save()
            return True

        if action == SystemAction.SELECT_ALL:
            self.keyboard.select_all()
            return True

        if action == SystemAction.SWITCH_APP:
            self.keyboard.switch_app()
            return True

        if action == SystemAction.NAV_UP:
            self.keyboard.navigate_up()
            return True
        
        if action == SystemAction.NAV_DOWN:
            self.keyboard.navigate_down()
            return True
        
        if action == SystemAction.NAV_LEFT:
            self.keyboard.navigate_left()
            return True
        
        if action == SystemAction.NAV_RIGHT:
            self.keyboard.navigate_right()
            return True

        return False