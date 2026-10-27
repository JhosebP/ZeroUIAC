import pytest

from modules.adaptation.reward_function import (
    RewardCalculator,
    RewardContext,
)


def test_neutral_context_returns_zero():

    calculator = RewardCalculator()

    reward = calculator.calculate(
        RewardContext()
    )

    assert reward == 0.0


def test_success_has_positive_reward():

    calculator = RewardCalculator()

    reward = calculator.calculate(
        RewardContext(
            success=True
        )
    )

    assert reward == 1.0


def test_error_has_strong_penalty():

    calculator = RewardCalculator()

    reward = calculator.calculate(
        RewardContext(
            error=True
        )
    )

    assert reward == -2.0


def test_error_outweighs_success():

    calculator = RewardCalculator()

    reward = calculator.calculate(
        RewardContext(
            success=True,
            error=True,
        )
    )

    assert reward < 0.0


def test_normal_latency_has_no_penalty():

    calculator = RewardCalculator()

    reward = calculator.calculate(
        RewardContext(
            success=True,
            latency_seconds=1.0,
        )
    )

    assert reward == 1.0


def test_high_latency_reduces_reward():

    calculator = RewardCalculator()

    reward = calculator.calculate(
        RewardContext(
            success=True,
            latency_seconds=3.0,
        )
    )

    assert reward < 1.0

    assert reward > 0.0


def test_small_switch_rate_has_no_penalty():

    calculator = RewardCalculator()

    reward = calculator.calculate(
        RewardContext(
            success=True,
            switch_rate=2.0,
        )
    )

    assert reward == 1.0


def test_high_switch_rate_reduces_reward():

    calculator = RewardCalculator()

    reward = calculator.calculate(
        RewardContext(
            success=True,
            switch_rate=6.0,
        )
    )

    assert reward < 1.0


def test_fatigue_reduces_reward():

    calculator = RewardCalculator()

    without_fatigue = (
        calculator.calculate(
            RewardContext(
                success=True,
                fatigue_level=0.0,
            )
        )
    )

    with_fatigue = (
        calculator.calculate(
            RewardContext(
                success=True,
                fatigue_level=0.8,
            )
        )
    )

    assert (
        with_fatigue
        < without_fatigue
    )


def test_fatigue_is_clamped():

    calculator = RewardCalculator()

    reward_one = calculator.calculate(
        RewardContext(
            fatigue_level=1.0,
        )
    )

    reward_excess = calculator.calculate(
        RewardContext(
            fatigue_level=100.0,
        )
    )

    assert (
        reward_one
        == reward_excess
    )


def test_negative_values_do_not_create_bonus():

    calculator = RewardCalculator()

    reward = calculator.calculate(
        RewardContext(
            latency_seconds=-5.0,
            switch_rate=-10.0,
            fatigue_level=-1.0,
        )
    )

    assert reward == 0.0


def test_reward_is_bounded():

    calculator = RewardCalculator()

    reward = calculator.calculate(
        RewardContext(
            success=False,
            error=True,
            latency_seconds=100.0,
            switch_rate=100.0,
            fatigue_level=1.0,
        )
    )

    assert (
        calculator.MIN_REWARD
        <= reward
        <= calculator.MAX_REWARD
    )


def test_invalid_context_is_rejected():

    calculator = RewardCalculator()

    with pytest.raises(
        ValueError
    ):

        calculator.calculate(
            "contexto_invalido"
        )

def test_action_failures_reduce_reward():

    calculator = (
        RewardCalculator()
    )

    clean = calculator.calculate(
        RewardContext(
            success=True
        )
    )

    with_failures = (
        calculator.calculate(
            RewardContext(
                success=True,
                action_failure_rate=0.5,
            )
        )
    )

    assert (
        with_failures
        < clean
    )


def test_drag_failure_has_penalty():

    calculator = (
        RewardCalculator()
    )

    reward = calculator.calculate(
        RewardContext(
            success=True,
            drag_failure_rate=1.0,
        )
    )

    assert reward < 1.0


def test_cursor_corrections_reduce_reward():

    calculator = (
        RewardCalculator()
    )

    clean = calculator.calculate(
        RewardContext(
            success=True,
            correction_rate=0.0,
        )
    )

    unstable = calculator.calculate(
        RewardContext(
            success=True,
            correction_rate=0.8,
        )
    )

    assert unstable < clean


def test_outcome_rates_are_clamped():

    calculator = (
        RewardCalculator()
    )

    normal = calculator.calculate(
        RewardContext(
            action_failure_rate=1.0,
            drag_failure_rate=1.0,
            correction_rate=1.0,
        )
    )

    excessive = calculator.calculate(
        RewardContext(
            action_failure_rate=100.0,
            drag_failure_rate=100.0,
            correction_rate=100.0,
        )
    )

    assert normal == excessive