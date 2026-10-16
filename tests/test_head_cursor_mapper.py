from modules.vision.head_cursor_mapper import (
    HeadCursorMapper,
)


def create_mapper():

    return HeadCursorMapper(
        sensitivity_x=2.0,
        sensitivity_y=2.0,
        dead_zone=2.0,
        max_step=100,
        smoothing=1.0,
    )


def test_default_factor_preserves_base_behavior():

    mapper = create_mapper()

    dx, dy = mapper.calculate(
        yaw=12.0,
        pitch=0.0,
        neutral_yaw=0.0,
        neutral_pitch=0.0,
    )

    assert dx == -20
    assert dy == 0


def test_factor_above_one_increases_head_movement():

    mapper = create_mapper()

    dx, _ = mapper.calculate(
        yaw=12.0,
        pitch=0.0,
        neutral_yaw=0.0,
        neutral_pitch=0.0,
        sensitivity_factor=1.05,
    )

    assert dx == -21


def test_factor_below_one_reduces_head_movement():

    mapper = create_mapper()

    dx, _ = mapper.calculate(
        yaw=12.0,
        pitch=0.0,
        neutral_yaw=0.0,
        neutral_pitch=0.0,
        sensitivity_factor=0.95,
    )

    assert dx == -19


def test_factor_affects_vertical_movement():

    mapper = create_mapper()

    _, dy = mapper.calculate(
        yaw=0.0,
        pitch=12.0,
        neutral_yaw=0.0,
        neutral_pitch=0.0,
        sensitivity_factor=1.05,
    )

    assert dy == 21


def test_adaptive_factor_does_not_modify_base_sensitivity():

    mapper = create_mapper()

    mapper.calculate(
        yaw=12.0,
        pitch=12.0,
        neutral_yaw=0.0,
        neutral_pitch=0.0,
        sensitivity_factor=1.40,
    )

    assert mapper.sensitivity_x == 2.0
    assert mapper.sensitivity_y == 2.0


def test_invalid_factor_uses_neutral_factor():

    mapper = create_mapper()

    dx, _ = mapper.calculate(
        yaw=12.0,
        pitch=0.0,
        neutral_yaw=0.0,
        neutral_pitch=0.0,
        sensitivity_factor="invalido",
    )

    assert dx == -20


def test_non_positive_factor_uses_neutral_factor():

    mapper = create_mapper()

    dx, _ = mapper.calculate(
        yaw=12.0,
        pitch=0.0,
        neutral_yaw=0.0,
        neutral_pitch=0.0,
        sensitivity_factor=0.0,
    )

    assert dx == -20