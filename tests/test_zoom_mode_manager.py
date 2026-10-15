from application.interaction.zoom_mode_manager import (
    ZoomModeManager
)


def test_zoom_mode_disabled_by_default():

    manager = ZoomModeManager()

    assert manager.is_enabled() is False


def test_zoom_mode_can_be_enabled():

    manager = ZoomModeManager()

    manager.enable()

    assert manager.is_enabled() is True


def test_zoom_mode_can_be_disabled():

    manager = ZoomModeManager()

    manager.enable()

    manager.disable()

    assert manager.is_enabled() is False