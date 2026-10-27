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

def test_yaw_dead_zone_stops_horizontal_axis_while_pitch_stays_smoothed():
    import pytest

    mapper = HeadCursorMapper()
    assert mapper.calculate(12.0, 12.0, 0.0, 0.0) == (-7, 7)
    dx, dy = mapper.calculate(2.0, 12.0, 0.0, 0.0)
    assert dx == 0
    assert dy == 11
    assert mapper.previous_dx == 0.0
    assert mapper.previous_dy == pytest.approx(11.55)
    assert mapper.calculate(1.0, 12.0, 0.0, 0.0) == (0, 14)


def test_pitch_dead_zone_stops_vertical_axis_while_yaw_stays_smoothed():
    import pytest

    mapper = HeadCursorMapper()
    assert mapper.calculate(12.0, 12.0, 0.0, 0.0) == (-7, 7)
    dx, dy = mapper.calculate(12.0, -2.0, 0.0, 0.0)
    assert dx == -11
    assert dy == 0
    assert mapper.previous_dx == pytest.approx(-11.55)
    assert mapper.previous_dy == 0.0
    assert mapper.calculate(12.0, -1.0, 0.0, 0.0) == (-14, 0)


def test_both_neutral_axes_clear_smoothing_memory():
    mapper = HeadCursorMapper()
    for _ in range(5):
        mapper.calculate(12.0, -12.0, 0.0, 0.0)
    assert mapper.previous_dx != 0.0
    assert mapper.previous_dy != 0.0

    assert mapper.calculate(2.0, -2.0, 0.0, 0.0) == (0, 0)
    assert mapper.previous_dx == 0.0
    assert mapper.previous_dy == 0.0
    # Re-entry starts from zero, without inheriting the opposite direction.
    assert mapper.calculate(-12.0, 12.0, 0.0, 0.0) == (7, 7)


def test_horizontal_reentry_does_not_reuse_previous_movement():
    mapper = HeadCursorMapper()
    for _ in range(5):
        mapper.calculate(12.0, 12.0, 0.0, 0.0)
    assert mapper.calculate(0.0, 12.0, 0.0, 0.0)[0] == 0
    assert mapper.calculate(-12.0, 12.0, 0.0, 0.0)[0] == 7


def test_vertical_reentry_does_not_reuse_previous_movement():
    mapper = HeadCursorMapper()
    for _ in range(5):
        mapper.calculate(12.0, 12.0, 0.0, 0.0)
    assert mapper.calculate(12.0, 0.0, 0.0, 0.0)[1] == 0
    assert mapper.calculate(12.0, -12.0, 0.0, 0.0)[1] == -7


def test_active_axis_keeps_adaptive_factor_limit_and_real_smoothing():
    import pytest

    mapper = HeadCursorMapper(max_step=10)
    # Target is (12 - 2) * 2 * 1.4 = 28, limited to 10 before smoothing.
    assert mapper.calculate(12.0, 0.0, 0.0, 0.0, 1.4) == (-3, 0)
    assert mapper.previous_dx == pytest.approx(-3.5)
    assert mapper.calculate(12.0, 0.0, 0.0, 0.0, 1.4) == (-5, 0)
    assert mapper.previous_dx == pytest.approx(-5.775)
    assert mapper.smoothing == 0.35
    assert mapper.sensitivity_x == 2.0

    mapper = HeadCursorMapper()
    assert mapper.calculate(12.0, 0.0, 0.0, 0.0, 1.4) == (-9, 0)
    assert mapper.previous_dx == pytest.approx(-9.8)
