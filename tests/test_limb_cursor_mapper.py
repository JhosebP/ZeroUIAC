from modules.vision.limb_cursor_mapper import (
    LimbCursorMapper
)


def test_center_maps_to_center():

    mapper = LimbCursorMapper(
        margin=0.0,
        smoothing=1.0,
        min_movement=0
    )

    x, y = mapper.calculate(
        hand_x=0.5,
        hand_y=0.5,
        screen_width=1000,
        screen_height=800
    )

    assert 490 <= x <= 510
    assert 390 <= y <= 410


def test_right_moves_right():

    mapper = LimbCursorMapper(
        margin=0.0,
        smoothing=1.0,
        min_movement=0
    )

    x_center, _ = mapper.calculate(
        0.5,
        0.5,
        1000,
        800
    )

    mapper.reset()

    x_right, _ = mapper.calculate(
        0.8,
        0.5,
        1000,
        800
    )

    assert x_right > x_center


def test_left_moves_left():

    mapper = LimbCursorMapper(
        margin=0.0,
        smoothing=1.0,
        min_movement=0
    )

    x_center, _ = mapper.calculate(
        0.5,
        0.5,
        1000,
        800
    )

    mapper.reset()

    x_left, _ = mapper.calculate(
        0.2,
        0.5,
        1000,
        800
    )

    assert x_left < x_center


def test_up_moves_up():

    mapper = LimbCursorMapper(
        margin=0.0,
        smoothing=1.0,
        min_movement=0
    )

    _, y_center = mapper.calculate(
        0.5,
        0.5,
        1000,
        800
    )

    mapper.reset()

    _, y_up = mapper.calculate(
        0.5,
        0.2,
        1000,
        800
    )

    assert y_up < y_center


def test_down_moves_down():

    mapper = LimbCursorMapper(
        margin=0.0,
        smoothing=1.0,
        min_movement=0
    )

    _, y_center = mapper.calculate(
        0.5,
        0.5,
        1000,
        800
    )

    mapper.reset()

    _, y_down = mapper.calculate(
        0.5,
        0.8,
        1000,
        800
    )

    assert y_down > y_center