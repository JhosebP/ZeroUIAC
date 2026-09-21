from unittest.mock import Mock

from application.interaction.action_executor import (
    ActionExecutor
)

from domain.commands.system_actions import (
    SystemAction
)


def create_executor():

    mouse = Mock()
    keyboard = Mock()

    executor = ActionExecutor(
        mouse,
        keyboard
    )

    return executor, mouse, keyboard


def test_left_click():

    executor, mouse, _ = (
        create_executor()
    )

    result = executor.execute(
        SystemAction.LEFT_CLICK
    )

    mouse.left_click.assert_called_once()

    assert result is True


def test_right_click():

    executor, mouse, _ = (
        create_executor()
    )

    result = executor.execute(
        SystemAction.RIGHT_CLICK
    )

    mouse.right_click.assert_called_once()

    assert result is True


def test_double_click():

    executor, mouse, _ = (
        create_executor()
    )

    executor.execute(
        SystemAction.DOUBLE_CLICK
    )

    mouse.double_click.assert_called_once()


def test_start_drag():

    executor, mouse, _ = (
        create_executor()
    )

    executor.execute(
        SystemAction.START_DRAG
    )

    mouse.start_drag.assert_called_once()


def test_stop_drag():

    executor, mouse, _ = (
        create_executor()
    )

    executor.execute(
        SystemAction.STOP_DRAG
    )

    mouse.stop_drag.assert_called_once()


def test_copy():

    executor, _, keyboard = (
        create_executor()
    )

    executor.execute(
        SystemAction.COPY
    )

    keyboard.copy.assert_called_once()


def test_paste():

    executor, _, keyboard = (
        create_executor()
    )

    executor.execute(
        SystemAction.PASTE
    )

    keyboard.paste.assert_called_once()


def test_cut():

    executor, _, keyboard = (
        create_executor()
    )

    executor.execute(
        SystemAction.CUT
    )

    keyboard.cut.assert_called_once()


def test_undo():

    executor, _, keyboard = (
        create_executor()
    )

    executor.execute(
        SystemAction.UNDO
    )

    keyboard.undo.assert_called_once()


def test_save():

    executor, _, keyboard = (
        create_executor()
    )

    executor.execute(
        SystemAction.SAVE
    )

    keyboard.save.assert_called_once()


def test_select_all():

    executor, _, keyboard = (
        create_executor()
    )

    executor.execute(
        SystemAction.SELECT_ALL
    )

    keyboard.select_all.assert_called_once()


def test_switch_app():

    executor, _, keyboard = (
        create_executor()
    )

    executor.execute(
        SystemAction.SWITCH_APP
    )

    keyboard.switch_app.assert_called_once()