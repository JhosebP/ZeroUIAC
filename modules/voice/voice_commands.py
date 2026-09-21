from domain.commands.system_actions import (
    SystemAction
)


VOICE_COMMANDS = [
    "clic",
    "clic derecho",
    "doble clic",
    "copiar",
    "pegar",
    "cortar",
    "deshacer",
    "guardar",
    "seleccionar todo",
    "cambiar aplicacion",
    "arrastrar",
    "soltar",
    "arriba",
    "abajo",
    "izquierda",
    "derecha",
    "acercar",
    "alejar",
    "dibujar",
    "borrar"
]


VOICE_ACTION_MAP = {

    "clic":
        SystemAction.LEFT_CLICK,

    "clic derecho":
        SystemAction.RIGHT_CLICK,

    "doble clic":
        SystemAction.DOUBLE_CLICK,

    "copiar":
        SystemAction.COPY,

    "pegar":
        SystemAction.PASTE,

    "cortar":
        SystemAction.CUT,

    "deshacer":
        SystemAction.UNDO,

    "guardar":
        SystemAction.SAVE,

    "seleccionar todo":
        SystemAction.SELECT_ALL,

    "cambiar aplicacion":
        SystemAction.SWITCH_APP,

    "arrastrar":
        SystemAction.START_DRAG,

    "soltar":
        SystemAction.STOP_DRAG,

    "arriba":
        SystemAction.NAV_UP,

    "abajo":
        SystemAction.NAV_DOWN,

    "izquierda":
        SystemAction.NAV_LEFT,

    "derecha":
        SystemAction.NAV_RIGHT,

    # Estos cuatro comandos son reconocidos
    # desde ahora, pero sus funcionalidades
    # corresponden al Sprint 3.
    "acercar": None,
    "alejar": None,
    "dibujar": None,
    "borrar": None,
}