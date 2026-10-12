from domain.commands.system_actions import (
    SystemAction
)

from modules.vision.head_zoom_detector import (
    HeadZoomDetector
)


def create_detector():

    return HeadZoomDetector(
        threshold=10.0,
        release_threshold=3.0,
        stable_frames=3,
        cooldown=0.0
    )


def test_forward_head_movement_zooms_in():

    detector = (
        create_detector()
    )

    assert (
        detector.detect(
            pitch=12.0,
            neutral_pitch=0.0
        )
        is None
    )

    assert (
        detector.detect(
            pitch=12.0,
            neutral_pitch=0.0
        )
        is None
    )

    result = (
        detector.detect(
            pitch=12.0,
            neutral_pitch=0.0
        )
    )

    assert (
        result
        == SystemAction.ZOOM_IN
    )


def test_backward_head_movement_zooms_out():

    detector = (
        create_detector()
    )

    detector.detect(
        pitch=-12.0,
        neutral_pitch=0.0
    )

    detector.detect(
        pitch=-12.0,
        neutral_pitch=0.0
    )

    result = (
        detector.detect(
            pitch=-12.0,
            neutral_pitch=0.0
        )
    )

    assert (
        result
        == SystemAction.ZOOM_OUT
    )


def test_held_head_position_does_not_repeat():

    detector = (
        create_detector()
    )

    for _ in range(3):

        detector.detect(
            pitch=12.0,
            neutral_pitch=0.0
        )

    result = (
        detector.detect(
            pitch=12.0,
            neutral_pitch=0.0
        )
    )

    assert result is None


def test_zoom_can_trigger_again_after_neutral():

    detector = (
        create_detector()
    )

    for _ in range(3):

        detector.detect(
            pitch=12.0,
            neutral_pitch=0.0
        )

    detector.detect(
        pitch=0.0,
        neutral_pitch=0.0
    )

    detector.detect(
        pitch=12.0,
        neutral_pitch=0.0
    )

    detector.detect(
        pitch=12.0,
        neutral_pitch=0.0
    )

    result = (
        detector.detect(
            pitch=12.0,
            neutral_pitch=0.0
        )
    )

    assert (
        result
        == SystemAction.ZOOM_IN
    )

def test_zoom_candidate_marks_detector_as_active():

    detector = (
        create_detector()
    )

    result = (
        detector.detect(
            pitch=12.0,
            neutral_pitch=0.0
        )
    )

    assert result is None

    assert (
        detector.is_active
        is True
    )