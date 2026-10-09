from enum import Enum


class SystemAction(str, Enum):
    """
    Acciones internas que ZeroUI-AC puede
    ejecutar sobre el sistema operativo.
    """

    # Mouse
    LEFT_CLICK = "left_click"
    RIGHT_CLICK = "right_click"
    DOUBLE_CLICK = "double_click"

    START_DRAG = "start_drag"
    STOP_DRAG = "stop_drag"

    # Teclado / atajos
    COPY = "copy"
    PASTE = "paste"
    CUT = "cut"
    UNDO = "undo"
    SAVE = "save"
    SELECT_ALL = "select_all"
    SWITCH_APP = "switch_app"

    # Navegación
    NAV_UP = "nav_up"
    NAV_DOWN = "nav_down"
    NAV_LEFT = "nav_left"
    NAV_RIGHT = "nav_right"
    
    DRAW = "draw"
    ERASE = "erase"

    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"