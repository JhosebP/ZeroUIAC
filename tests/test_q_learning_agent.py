import pytest

from modules.adaptation.adaptive_actions import (
    AdaptiveAction,
)

from modules.adaptation.adaptive_state import (
    AdaptiveState,
)

from modules.adaptation.q_learning_agent import (
    QLearningAgent,
)


def create_state(
    error="low",
    activity="low",
    switches="low",
    source="head",
    stage="short",
):

    return AdaptiveState(
        voice_error_level=error,
        activity_level=activity,
        switch_level=switches,
        dominant_source=source,
        session_stage=stage,
    )


def test_new_q_value_starts_at_zero():

    agent = QLearningAgent(
        seed=1
    )

    state = create_state()

    value = agent.get_q_value(
        state,
        AdaptiveAction.NO_CHANGE,
    )

    assert value == 0.0


def test_q_value_can_be_set():

    agent = QLearningAgent()

    state = create_state()

    agent.set_q_value(
        state,
        AdaptiveAction
        .INCREASE_HEAD_SENSITIVITY,
        2.5,
    )

    assert (
        agent.get_q_value(
            state,
            AdaptiveAction
            .INCREASE_HEAD_SENSITIVITY,
        )
        == 2.5
    )


def test_exploitation_selects_best_action():

    agent = QLearningAgent(
        epsilon=0.0,
        epsilon_min=0.0,
        seed=1,
    )

    state = create_state()

    agent.set_q_value(
        state,
        AdaptiveAction
        .DECREASE_HEAD_SENSITIVITY,
        10.0,
    )

    action = agent.choose_action(
        state
    )

    assert (
        action
        == AdaptiveAction
        .DECREASE_HEAD_SENSITIVITY
    )


def test_exploration_returns_valid_action():

    agent = QLearningAgent(
        epsilon=1.0,
        epsilon_min=0.0,
        seed=1,
    )

    state = create_state()

    action = agent.choose_action(
        state
    )

    assert isinstance(
        action,
        AdaptiveAction,
    )


def test_positive_reward_increases_q_value():

    agent = QLearningAgent(
        learning_rate=0.5,
        discount_factor=0.0,
    )

    state = create_state()

    next_state = create_state(
        activity="medium"
    )

    value = agent.update(
        state=state,
        action=(
            AdaptiveAction
            .DECREASE_HEAD_SENSITIVITY
        ),
        reward=1.0,
        next_state=next_state,
    )

    assert value > 0.0


def test_negative_reward_decreases_q_value():

    agent = QLearningAgent(
        learning_rate=0.5,
        discount_factor=0.0,
    )

    state = create_state()

    next_state = create_state(
        activity="medium"
    )

    value = agent.update(
        state=state,
        action=(
            AdaptiveAction
            .INCREASE_HEAD_SENSITIVITY
        ),
        reward=-2.0,
        next_state=next_state,
    )

    assert value < 0.0


def test_update_matches_q_learning_formula():

    agent = QLearningAgent(
        learning_rate=0.5,
        discount_factor=0.9,
    )

    state = create_state()

    next_state = create_state(
        activity="high"
    )

    agent.set_q_value(
        state,
        AdaptiveAction.NO_CHANGE,
        1.0,
    )

    agent.set_q_value(
        next_state,
        AdaptiveAction
        .INCREASE_LIMB_SENSITIVITY,
        2.0,
    )

    new_value = agent.update(
        state=state,
        action=AdaptiveAction.NO_CHANGE,
        reward=1.0,
        next_state=next_state,
    )

    # 1 + 0.5 * (
    #   1 + 0.9 * 2 - 1
    # )
    # = 1.9

    assert new_value == pytest.approx(
        1.9
    )


def test_terminal_state_ignores_future_q():

    agent = QLearningAgent(
        learning_rate=1.0,
        discount_factor=0.9,
    )

    state = create_state()

    next_state = create_state(
        stage="long"
    )

    agent.set_q_value(
        next_state,
        AdaptiveAction.NO_CHANGE,
        100.0,
    )

    value = agent.update(
        state=state,
        action=AdaptiveAction.NO_CHANGE,
        reward=2.0,
        next_state=next_state,
        terminal=True,
    )

    assert value == 2.0


def test_decay_reduces_epsilon():

    agent = QLearningAgent(
        epsilon=0.5,
        epsilon_min=0.1,
        epsilon_decay=0.5,
    )

    new_epsilon = (
        agent.decay_exploration()
    )

    assert new_epsilon == 0.25


def test_epsilon_never_goes_below_minimum():

    agent = QLearningAgent(
        epsilon=0.2,
        epsilon_min=0.1,
        epsilon_decay=0.1,
    )

    for _ in range(20):

        agent.decay_exploration()

    assert agent.epsilon == 0.1


def test_state_values_returns_all_actions():

    agent = QLearningAgent()

    values = agent.get_state_values(
        create_state()
    )

    assert (
        len(values)
        == len(AdaptiveAction)
    )

    assert (
        AdaptiveAction.NO_CHANGE
        in values
    )


def test_q_table_snapshot_is_copy():

    agent = QLearningAgent()

    state = create_state()

    agent.set_q_value(
        state,
        AdaptiveAction.NO_CHANGE,
        5.0,
    )

    snapshot = (
        agent.get_q_table_snapshot()
    )

    snapshot[
        state.as_key()
    ][
        AdaptiveAction.NO_CHANGE
    ] = 999.0

    assert (
        agent.get_q_value(
            state,
            AdaptiveAction.NO_CHANGE,
        )
        == 5.0
    )


def test_invalid_action_is_rejected():

    agent = QLearningAgent()

    with pytest.raises(
        ValueError
    ):

        agent.get_q_value(
            create_state(),
            "accion_invalida",
        )


def test_none_state_is_rejected():

    agent = QLearningAgent()

    with pytest.raises(
        ValueError
    ):

        agent.choose_action(
            None
        )


def test_invalid_learning_rate_is_rejected():

    with pytest.raises(
        ValueError
    ):

        QLearningAgent(
            learning_rate=2.0
        )


def test_invalid_epsilon_configuration_is_rejected():

    with pytest.raises(
        ValueError
    ):

        QLearningAgent(
            epsilon=0.1,
            epsilon_min=0.5,
        )