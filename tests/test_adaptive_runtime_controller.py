import pytest

from modules.adaptation.adaptive_actions import (
    AdaptiveAction
)

from modules.adaptation.adaptive_action_applier import (
    AdaptiveActionApplier
)

from modules.adaptation.adaptive_parameters import (
    AdaptiveParametersManager
)

from modules.adaptation.adaptive_channel_weights import (
    AdaptiveChannelWeights
)

from modules.adaptation.adaptive_state import (
    AdaptiveStateBuilder
)

from modules.adaptation.q_learning_agent import (
    QLearningAgent
)

from modules.adaptation.adaptive_runtime_controller import (
    AdaptiveRuntimeController
)


class FakeSessionManager:

    def __init__(
        self,
        snapshot=None
    ):

        self.snapshot = snapshot

    def get_snapshot(self):

        return self.snapshot


def create_snapshot(
    duration=0.0,
    voice=0,
    head=0,
    limb=0,
    gesture=0,
    errors=0,
    switches=0,
    action_events=0,
    action_interval=0.0,
    action_interval_samples=0,
):

    return {
        "session_id": "test",

        "metrics": {

            "duration_seconds":
                duration,

            "total_events": (
                voice
                + head
                + limb
                + gesture
            ),

            "action_events":
                action_events,

            "error_events":
                errors,

            "voice_error_events":
                errors,

            "voice_error_rate": (
                errors / voice
                if voice > 0
                else 0.0
            ),

            "user_channel_switches":
                switches,

            "channel_switches":
                switches,

            "average_action_interval_seconds":
                action_interval,

            "action_interval_samples":
                action_interval_samples,

            "average_movement_magnitude":
                0.0,

            "movement_variability":
                0.0,

            "movement_samples":
                0,

            "source_counts": {
                "voice": voice,
                "head": head,
                "limb": limb,
                "gesture": gesture,
                "system": 0,
            }
        }
    }


def create_controller(
    manager,
    clock,
    interval=30.0,
):

    parameters = (
        AdaptiveParametersManager()
    )

    weights = (
        AdaptiveChannelWeights()
    )

    applier = (
        AdaptiveActionApplier(
            parameters_manager=parameters,
            channel_weights=weights,
        )
    )

    agent = QLearningAgent(
        epsilon=0.0,
        epsilon_min=0.0,
        seed=1,
    )

    controller = (
        AdaptiveRuntimeController(
            session_manager=manager,
            action_applier=applier,
            q_agent=agent,
            adaptation_interval_seconds=(
                interval
            ),
            clock=clock,
        )
    )

    return (
        controller,
        agent,
        parameters,
        weights
    )


def test_first_step_only_creates_baseline():

    clock_value = [0.0]

    manager = FakeSessionManager(
        create_snapshot()
    )

    (
        controller,
        _,
        parameters,
        _
    ) = create_controller(
        manager,
        lambda: clock_value[0]
    )

    result = controller.step(
        force=True
    )

    assert result is None

    assert (
        parameters.snapshot()
        .head_sensitivity_factor
        == 1.0
    )


def test_interval_blocks_early_adaptation():

    clock_value = [0.0]

    manager = FakeSessionManager(
        create_snapshot()
    )

    (
        controller,
        _,
        _,
        _
    ) = create_controller(
        manager,
        lambda: clock_value[0]
    )

    controller.step()

    manager.snapshot = (
        create_snapshot(
            duration=10.0,
            voice=1,
            action_events=1,
        )
    )

    clock_value[0] = 10.0

    assert (
        controller.step()
        is None
    )


def test_new_q_table_prefers_no_change():

    clock_value = [0.0]

    manager = FakeSessionManager(
        create_snapshot()
    )

    (
        controller,
        _,
        parameters,
        weights
    ) = create_controller(
        manager,
        lambda: clock_value[0],
        interval=0.0,
    )

    controller.step()

    manager.snapshot = (
        create_snapshot(
            duration=30.0,
            voice=1,
            action_events=1,
        )
    )

    result = controller.step()

    assert (
        result.action
        == AdaptiveAction.NO_CHANGE
    )

    assert result.changed is False

    assert (
        parameters.snapshot()
        .head_sensitivity_factor
        == 1.0
    )

    assert (
        weights.snapshot().voice
        == 1.0
    )


def test_learned_head_action_changes_one_step():

    clock_value = [0.0]

    manager = FakeSessionManager(
        create_snapshot()
    )

    (
        controller,
        agent,
        parameters,
        _
    ) = create_controller(
        manager,
        lambda: clock_value[0],
        interval=0.0,
    )

    controller.step()

    manager.snapshot = (
        create_snapshot(
            duration=30.0,
            head=10,
        )
    )

    state = (
        AdaptiveStateBuilder()
        .build(
            manager.snapshot
        )
    )

    agent.set_q_value(
        state,
        AdaptiveAction
        .INCREASE_HEAD_SENSITIVITY,
        10.0,
    )

    result = controller.step()

    assert (
        result.action
        == AdaptiveAction
        .INCREASE_HEAD_SENSITIVITY
    )

    assert (
        parameters.snapshot()
        .head_sensitivity_factor
        == 1.05
    )


def test_learned_voice_weight_changes_one_step():

    clock_value = [0.0]

    manager = FakeSessionManager(
        create_snapshot()
    )

    (
        controller,
        agent,
        _,
        weights
    ) = create_controller(
        manager,
        lambda: clock_value[0],
        interval=0.0,
    )

    controller.step()

    manager.snapshot = (
        create_snapshot(
            duration=30.0,
            voice=10,
        )
    )

    state = (
        AdaptiveStateBuilder()
        .build(
            manager.snapshot
        )
    )

    agent.set_q_value(
        state,
        AdaptiveAction
        .INCREASE_VOICE_WEIGHT,
        10.0,
    )

    result = controller.step()

    assert (
        result.action
        == AdaptiveAction
        .INCREASE_VOICE_WEIGHT
    )

    assert (
        weights.snapshot().voice
        == 1.05
    )


def test_second_window_updates_q_value():

    clock_value = [0.0]

    manager = FakeSessionManager(
        create_snapshot()
    )

    (
        controller,
        agent,
        _,
        _
    ) = create_controller(
        manager,
        lambda: clock_value[0],
        interval=0.0,
    )

    controller.step()

    manager.snapshot = (
        create_snapshot(
            duration=30.0,
            voice=1,
            action_events=1,
        )
    )

    first_result = (
        controller.step()
    )

    assert (
        first_result.action
        == AdaptiveAction.NO_CHANGE
    )

    manager.snapshot = (
        create_snapshot(
            duration=60.0,
            voice=2,
            action_events=2,
        )
    )

    second_result = (
        controller.step()
    )

    assert (
        second_result.reward
        is not None
    )

    assert (
        agent.get_q_value(
            first_result.state_key,
            AdaptiveAction.NO_CHANGE,
        )
        > 0.0
    )


def test_finalize_learns_without_new_action():

    clock_value = [0.0]

    manager = FakeSessionManager(
        create_snapshot()
    )

    (
        controller,
        agent,
        parameters,
        _
    ) = create_controller(
        manager,
        lambda: clock_value[0],
        interval=0.0,
    )

    controller.step()

    manager.snapshot = (
        create_snapshot(
            duration=30.0,
            head=5,
        )
    )

    state = (
        AdaptiveStateBuilder()
        .build(
            manager.snapshot
        )
    )

    agent.set_q_value(
        state,
        AdaptiveAction
        .INCREASE_HEAD_SENSITIVITY,
        10.0,
    )

    controller.step()

    assert (
        parameters.snapshot()
        .head_sensitivity_factor
        == 1.05
    )

    manager.snapshot = (
        create_snapshot(
            duration=60.0,
            head=10,
        )
    )

    reward = (
        controller.finalize()
    )

    assert reward is not None

    # finalize aprende,
    # pero no aplica otro paso.
    assert (
        parameters.snapshot()
        .head_sensitivity_factor
        == 1.05
    )


def test_start_requires_active_session():

    manager = FakeSessionManager(
        None
    )

    (
        controller,
        _,
        _,
        _
    ) = create_controller(
        manager,
        lambda: 0.0
    )

    assert (
        controller.start()
        is False
    )


def test_invalid_adaptation_interval_is_rejected():

    manager = FakeSessionManager(
        create_snapshot()
    )

    parameters = (
        AdaptiveParametersManager()
    )

    weights = (
        AdaptiveChannelWeights()
    )

    applier = (
        AdaptiveActionApplier(
            parameters_manager=parameters,
            channel_weights=weights,
        )
    )

    with pytest.raises(
        ValueError
    ):

        AdaptiveRuntimeController(
            session_manager=manager,
            action_applier=applier,
            adaptation_interval_seconds=-1,
        )