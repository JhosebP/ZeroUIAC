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

def test_feedback_is_empty_by_default():

    overlay = (
        AnnotationOverlay()
    )

    assert (
        overlay.feedback_text
        is None
    )


def test_show_feedback_stores_message():

    overlay = (
        AnnotationOverlay()
    )

    overlay.show_feedback(
        "Copiar"
    )

    assert (
        overlay.feedback_text
        == "Copiar"
    )


def test_default_feedback_duration_is_1_5_seconds():

    overlay = (
        AnnotationOverlay()
    )

    assert (
        overlay.feedback_duration
        == 1.5
    )

def test_error_feedback_is_marked_as_error():

    overlay = (
        AnnotationOverlay()
    )

    overlay.show_error_feedback(
        "Comando no reconocido"
    )

    assert (
        overlay.feedback_text
        == "Comando no reconocido"
    )

    assert (
        overlay.feedback_type
        == "error"
    )

def test_screen_to_canvas_uses_virtual_origin():

    overlay = AnnotationOverlay()

    overlay._virtual_left = -1920
    overlay._virtual_top = -200

    x, y = (
        overlay._screen_to_canvas(
            -1000,
            300
        )
    )

    assert x == 920
    assert y == 500


def test_virtual_geometry_supports_negative_origin():

    overlay = AnnotationOverlay()

    overlay._virtual_left = -1920
    overlay._virtual_top = -200

    overlay._virtual_width = 3840
    overlay._virtual_height = 1280

    geometry = (
        overlay._build_virtual_geometry()
    )

    assert (
        geometry
        == "3840x1280-1920-200"
    )  