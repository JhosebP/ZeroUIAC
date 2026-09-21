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

    assert len(VOICE_ACTION_MAP) == 20

    for command in VOICE_COMMANDS:
        assert command in VOICE_ACTION_MAP


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


def test_sprint_3_commands_are_pending():

    assert (
        VOICE_ACTION_MAP["acercar"]
        is None
    )

    assert (
        VOICE_ACTION_MAP["alejar"]
        is None
    )

    assert (
        VOICE_ACTION_MAP["dibujar"]
        is None
    )

    assert (
        VOICE_ACTION_MAP["borrar"]
        is None
    )