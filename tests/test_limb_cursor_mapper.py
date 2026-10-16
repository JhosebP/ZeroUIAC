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

def test_default_factor_preserves_limb_behavior():

    mapper = LimbCursorMapper(
        margin=0.0,
        smoothing=1.0,
        min_movement=0
    )

    x, _ = mapper.calculate(
        hand_x=0.8,
        hand_y=0.5,
        screen_width=1000,
        screen_height=800,
        sensitivity_factor=1.0
    )

    assert 790 <= x <= 810


def test_factor_above_one_increases_limb_range():

    mapper = LimbCursorMapper(
        margin=0.0,
        smoothing=1.0,
        min_movement=0
    )

    normal_x, _ = mapper.calculate(
        0.8,
        0.5,
        1000,
        800,
        sensitivity_factor=1.0
    )

    mapper.reset()

    increased_x, _ = mapper.calculate(
        0.8,
        0.5,
        1000,
        800,
        sensitivity_factor=1.20
    )

    assert increased_x > normal_x


def test_factor_below_one_reduces_limb_range():

    mapper = LimbCursorMapper(
        margin=0.0,
        smoothing=1.0,
        min_movement=0
    )

    normal_x, _ = mapper.calculate(
        0.8,
        0.5,
        1000,
        800,
        sensitivity_factor=1.0
    )

    mapper.reset()

    reduced_x, _ = mapper.calculate(
        0.8,
        0.5,
        1000,
        800,
        sensitivity_factor=0.80
    )

    assert reduced_x < normal_x


def test_factor_affects_vertical_limb_range():

    mapper = LimbCursorMapper(
        margin=0.0,
        smoothing=1.0,
        min_movement=0
    )

    _, normal_y = mapper.calculate(
        0.5,
        0.8,
        1000,
        800,
        sensitivity_factor=1.0
    )

    mapper.reset()

    _, increased_y = mapper.calculate(
        0.5,
        0.8,
        1000,
        800,
        sensitivity_factor=1.20
    )

    assert increased_y > normal_y


def test_center_remains_center_with_adaptation():

    mapper = LimbCursorMapper(
        margin=0.0,
        smoothing=1.0,
        min_movement=0
    )

    x, y = mapper.calculate(
        0.5,
        0.5,
        1000,
        800,
        sensitivity_factor=1.40
    )

    assert 490 <= x <= 510
    assert 390 <= y <= 410


def test_factor_does_not_modify_base_limb_sensitivity():

    mapper = LimbCursorMapper(
        margin=0.0,
        sensitivity_x=1.0,
        sensitivity_y=1.0,
        smoothing=1.0,
        min_movement=0
    )

    mapper.calculate(
        0.8,
        0.8,
        1000,
        800,
        sensitivity_factor=1.40
    )

    assert mapper.sensitivity_x == 1.0
    assert mapper.sensitivity_y == 1.0


def test_invalid_limb_factor_uses_neutral_value():

    mapper = LimbCursorMapper(
        margin=0.0,
        smoothing=1.0,
        min_movement=0
    )

    x, _ = mapper.calculate(
        0.8,
        0.5,
        1000,
        800,
        sensitivity_factor="invalido"
    )

    assert 790 <= x <= 810


def test_non_positive_limb_factor_uses_neutral_value():

    mapper = LimbCursorMapper(
        margin=0.0,
        smoothing=1.0,
        min_movement=0
    )

    x, _ = mapper.calculate(
        0.8,
        0.5,
        1000,
        800,
        sensitivity_factor=0.0
    )

    assert 790 <= x <= 810