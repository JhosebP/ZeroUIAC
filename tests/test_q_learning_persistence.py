import json

import pytest

from modules.adaptation.adaptive_actions import (
    AdaptiveAction
)

from modules.adaptation.adaptive_state import (
    AdaptiveState
)

from modules.adaptation.q_learning_agent import (
    QLearningAgent
)

from modules.adaptation.q_learning_persistence import (
    QLearningPersistence
)


def create_state():

    return AdaptiveState(
        voice_error_level="low",
        activity_level="medium",
        switch_level="low",
        dominant_source="head",
        session_stage="short",
    )


def test_missing_file_returns_false(
    tmp_path
):

    persistence = (
        QLearningPersistence(
            tmp_path
            / "q_learning.json"
        )
    )

    agent = QLearningAgent()

    assert (
        persistence.load(
            agent
        )
        is False
    )


def test_save_creates_json_file(
    tmp_path
):

    path = (
        tmp_path
        / "q_learning.json"
    )

    persistence = (
        QLearningPersistence(
            path
        )
    )

    agent = QLearningAgent()

    agent.set_q_value(
        create_state(),
        AdaptiveAction
        .DECREASE_HEAD_SENSITIVITY,
        2.5
    )

    assert (
        persistence.save(
            agent
        )
        is True
    )

    assert path.exists()


def test_saved_file_has_schema_version(
    tmp_path
):

    path = (
        tmp_path
        / "q_learning.json"
    )

    persistence = (
        QLearningPersistence(
            path
        )
    )

    agent = QLearningAgent()

    persistence.save(
        agent
    )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        data["schema_version"]
        == 1
    )


def test_q_value_is_restored(
    tmp_path
):

    path = (
        tmp_path
        / "q_learning.json"
    )

    persistence = (
        QLearningPersistence(
            path
        )
    )

    original_agent = (
        QLearningAgent()
    )

    state = create_state()

    original_agent.set_q_value(
        state,
        AdaptiveAction
        .INCREASE_HEAD_SENSITIVITY,
        3.75
    )

    persistence.save(
        original_agent
    )

    restored_agent = (
        QLearningAgent()
    )

    assert (
        persistence.load(
            restored_agent
        )
        is True
    )

    assert (
        restored_agent.get_q_value(
            state,
            AdaptiveAction
            .INCREASE_HEAD_SENSITIVITY
        )
        == 3.75
    )


def test_multiple_actions_are_restored(
    tmp_path
):

    path = (
        tmp_path
        / "q_learning.json"
    )

    persistence = (
        QLearningPersistence(
            path
        )
    )

    first = QLearningAgent()

    state = create_state()

    first.set_q_value(
        state,
        AdaptiveAction
        .INCREASE_HEAD_SENSITIVITY,
        1.5
    )

    first.set_q_value(
        state,
        AdaptiveAction
        .DECREASE_HEAD_SENSITIVITY,
        -2.0
    )

    persistence.save(
        first
    )

    second = QLearningAgent()

    persistence.load(
        second
    )

    assert (
        second.get_q_value(
            state,
            AdaptiveAction
            .INCREASE_HEAD_SENSITIVITY
        )
        == 1.5
    )

    assert (
        second.get_q_value(
            state,
            AdaptiveAction
            .DECREASE_HEAD_SENSITIVITY
        )
        == -2.0
    )


def test_epsilon_is_restored(
    tmp_path
):

    path = (
        tmp_path
        / "q_learning.json"
    )

    persistence = (
        QLearningPersistence(
            path
        )
    )

    first = QLearningAgent(
        epsilon=0.5,
        epsilon_min=0.02
    )

    first.epsilon = 0.23

    persistence.save(
        first
    )

    second = QLearningAgent(
        epsilon=0.5,
        epsilon_min=0.02
    )

    persistence.load(
        second
    )

    assert (
        second.epsilon
        == pytest.approx(
            0.23
        )
    )


def test_invalid_schema_is_rejected(
    tmp_path
):

    path = (
        tmp_path
        / "q_learning.json"
    )

    path.write_text(
        json.dumps(
            {
                "schema_version": 999,
                "q_table": []
            }
        ),
        encoding="utf-8"
    )

    persistence = (
        QLearningPersistence(
            path
        )
    )

    with pytest.raises(
        ValueError
    ):

        persistence.load(
            QLearningAgent()
        )


def test_corrupted_json_is_rejected(
    tmp_path
):

    path = (
        tmp_path
        / "q_learning.json"
    )

    path.write_text(
        "{esto no es json",
        encoding="utf-8"
    )

    persistence = (
        QLearningPersistence(
            path
        )
    )

    with pytest.raises(
        ValueError
    ):

        persistence.load(
            QLearningAgent()
        )