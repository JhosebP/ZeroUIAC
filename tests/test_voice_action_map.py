from domain.commands.system_actions import (
    SystemAction
)

from modules.voice.voice_commands import (
    VOICE_COMMANDS,
    VOICE_ACTION_MAP
)


def test_exactly_twenty_commands():

    assert len(VOICE_COMMANDS) == 20


def test_all_commands_are_mapped():

    for command in VOICE_COMMANDS:

        assert (
            command
            in VOICE_ACTION_MAP
        )


def test_click():

    assert (
        VOICE_ACTION_MAP["clic"]
        == SystemAction.LEFT_CLICK
    )


def test_right_click():

    assert (
        VOICE_ACTION_MAP["clic derecho"]
        == SystemAction.RIGHT_CLICK
    )


def test_double_click():

    assert (
        VOICE_ACTION_MAP["doble clic"]
        == SystemAction.DOUBLE_CLICK
    )


def test_copy():

    assert (
        VOICE_ACTION_MAP["copiar"]
        == SystemAction.COPY
    )


def test_paste():

    assert (
        VOICE_ACTION_MAP["pegar"]
        == SystemAction.PASTE
    )


def test_drag():

    assert (
        VOICE_ACTION_MAP["arrastrar"]
        == SystemAction.START_DRAG
    )


def test_drop():

    assert (
        VOICE_ACTION_MAP["soltar"]
        == SystemAction.STOP_DRAG
    )


def test_navigation():

    assert (
        VOICE_ACTION_MAP["arriba"]
        == SystemAction.NAV_UP
    )

    assert (
        VOICE_ACTION_MAP["abajo"]
        == SystemAction.NAV_DOWN
    )

    assert (
        VOICE_ACTION_MAP["izquierda"]
        == SystemAction.NAV_LEFT
    )

    assert (
        VOICE_ACTION_MAP["derecha"]
        == SystemAction.NAV_RIGHT
    )


def test_overlay_commands_are_mapped():

    assert (
        VOICE_ACTION_MAP["dibujar"]
        == SystemAction.DRAW
    )

def test_delete_command_is_mapped():

    assert (
        VOICE_ACTION_MAP["eliminar"]
        == SystemAction.DELETE
    )


def test_eraser_control_commands_are_mapped():

    assert (
        VOICE_ACTION_MAP[
            "activar borrador"
        ]
        == SystemAction.ERASER_ON
    )

    assert (
        VOICE_ACTION_MAP[
            "desactivar borrador"
        ]
        == SystemAction.ERASER_OFF
    )


def test_delete_replaces_old_borrar_command():

    assert "eliminar" in VOICE_COMMANDS
    assert "borrar" not in VOICE_COMMANDS
    assert len(VOICE_COMMANDS) == 20


def test_zoom_commands_are_mapped():

    assert (
        VOICE_ACTION_MAP["acercar"]
        == SystemAction.ZOOM_IN
    )

    assert (
        VOICE_ACTION_MAP["alejar"]
        == SystemAction.ZOOM_OUT
    )