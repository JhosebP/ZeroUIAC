from types import SimpleNamespace

from modules.vision.gesture_detector import (
    GestureDetector
)


def point(
    x,
    y,
    z=0.0
):
    return SimpleNamespace(
        x=x,
        y=y,
        z=z
    )


def create_hand(
    index=True,
    middle=True,
    ring=False,
    pinky=False
):
    landmarks = [
        point(0.5, 0.8)
        for _ in range(21)
    ]

    landmarks[0] = (
        point(0.5, 0.8)
    )

    finger_data = [
        (
            6,
            8,
            0.42,
            index
        ),
        (
            10,
            12,
            0.48,
            middle
        ),
        (
            14,
            16,
            0.54,
            ring
        ),
        (
            18,
            20,
            0.60,
            pinky
        )
    ]

    for (
        pip_index,
        tip_index,
        x,
        extended
    ) in finger_data:

        landmarks[
            pip_index
        ] = point(
            x,
            0.55
        )

        if extended:

            landmarks[
                tip_index
            ] = point(
                x,
                0.25
            )

        else:

            landmarks[
                tip_index
            ] = point(
                x,
                0.67
            )

    return SimpleNamespace(
        landmark=landmarks
    )


def test_draw_gesture():

    detector = (
        GestureDetector(
            stable_frames=2,
            cooldown=0
        )
    )

    hand = create_hand(
        index=True,
        middle=True,
        ring=False,
        pinky=False
    )

    assert (
        detector.detect(hand)
        is None
    )

    assert (
        detector.detect(hand)
        == GestureDetector
        .GESTURE_DRAW
    )


def test_erase_gesture():

    detector = (
        GestureDetector(
            stable_frames=2,
            cooldown=0
        )
    )

    hand = create_hand(
        index=True,
        middle=True,
        ring=True,
        pinky=False
    )

    detector.detect(
        hand
    )

    assert (
        detector.detect(hand)
        == GestureDetector
        .GESTURE_ERASE
    )


def test_held_gesture_does_not_repeat():

    detector = (
        GestureDetector(
            stable_frames=2,
            cooldown=0
        )
    )

    hand = create_hand()

    detector.detect(
        hand
    )

    assert (
        detector.detect(hand)
        == GestureDetector
        .GESTURE_DRAW
    )

    assert (
        detector.detect(hand)
        is None
    )

    assert (
        detector.detect(hand)
        is None
    )


def test_gesture_can_be_used_again_after_release():

    detector = (
        GestureDetector(
            stable_frames=2,
            cooldown=0
        )
    )

    draw_hand = (
        create_hand()
    )

    neutral_hand = (
        create_hand(
            index=True,
            middle=True,
            ring=True,
            pinky=True
        )
    )

    detector.detect(
        draw_hand
    )

    assert (
        detector.detect(
            draw_hand
        )
        == GestureDetector
        .GESTURE_DRAW
    )

    assert (
        detector.detect(
            neutral_hand
        )
        is None
    )

    detector.detect(
        draw_hand
    )

    assert (
        detector.detect(
            draw_hand
        )
        == GestureDetector
        .GESTURE_DRAW
    )


def test_open_hand_is_neutral():

    detector = (
        GestureDetector(
            stable_frames=2,
            cooldown=0
        )
    )

    hand = create_hand(
        index=True,
        middle=True,
        ring=True,
        pinky=True
    )

    assert (
        detector.detect(hand)
        is None
    )

    assert (
        detector.detect(hand)
        is None
    )