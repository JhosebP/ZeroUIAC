from presentation.overlay.annotation_overlay import (
    AnnotationOverlay
)


def test_overlay_inactive_by_default():

    overlay = AnnotationOverlay()

    assert overlay.is_active is False

    assert overlay.mode is None


def test_activate_draw_mode():

    overlay = AnnotationOverlay()

    overlay.toggle_draw()

    assert overlay.is_active is True

    assert (
        overlay.mode
        == AnnotationOverlay.MODE_DRAW
    )


def test_draw_toggle_deactivates_overlay():

    overlay = AnnotationOverlay()

    overlay.toggle_draw()
    overlay.toggle_draw()

    assert overlay.is_active is False

    assert overlay.mode is None


def test_activate_erase_mode():

    overlay = AnnotationOverlay()

    overlay.toggle_erase()

    assert overlay.is_active is True

    assert (
        overlay.mode
        == AnnotationOverlay.MODE_ERASE
    )


def test_erase_toggle_deactivates_overlay():

    overlay = AnnotationOverlay()

    overlay.toggle_erase()
    overlay.toggle_erase()

    assert overlay.is_active is False

    assert overlay.mode is None