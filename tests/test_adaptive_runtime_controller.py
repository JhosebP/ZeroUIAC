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

from modules.adaptation.interaction_outcome_tracker import (
    InteractionOutcomeTracker
)

from domain.commands.system_actions import (
    SystemAction
)

from domain.events.event_types import (
    EventSource,
    EventType
)

from domain.events.interaction_event import (
    InteractionEvent
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


def test_action_failure_reduces_window_reward():

    manager = FakeSessionManager(
        create_snapshot()
    )

    tracker = (
        InteractionOutcomeTracker()
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
            interaction_outcome_tracker=tracker,
            adaptation_interval_seconds=0.0,
            clock=lambda: 0.0,
        )
    )

    controller.step()

    manager.snapshot = (
        create_snapshot(
            duration=30.0,
            voice=1,
            action_events=1,
        )
    )

    controller.step()

    tracker.record_action_result(
        SystemAction.START_DRAG,
        False
    )

    manager.snapshot = (
        create_snapshot(
            duration=60.0,
            voice=2,
            action_events=2,
        )
    )

    result = controller.step()

    assert (
        result.reward
        < 0.0
    )


def test_cursor_corrections_reduce_reward():

    manager = FakeSessionManager(
        create_snapshot()
    )

    tracker = (
        InteractionOutcomeTracker()
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
            interaction_outcome_tracker=tracker,
            adaptation_interval_seconds=0.0,
            clock=lambda: 0.0,
        )
    )

    controller.step()

    manager.snapshot = (
        create_snapshot(
            duration=30.0,
            head=1,
        )
    )

    controller.step()

    tracker.record_cursor_event(
        InteractionEvent(
            source=EventSource.HEAD,
            event_type=EventType.CURSOR_MOVE,
            payload={
                "mode": "relative",
                "dx": 10,
                "dy": 0,
            }
        )
    )

    tracker.record_cursor_event(
        InteractionEvent(
            source=EventSource.HEAD,
            event_type=EventType.CURSOR_MOVE,
            payload={
                "mode": "relative",
                "dx": -10,
                "dy": 0,
            }
        )
    )

    manager.snapshot = (
        create_snapshot(
            duration=60.0,
            head=3,
        )
    )

    result = controller.step()

    assert (
        result.reward
        < 1.0
    )

@pytest.fixture
def window_runtime():
    from unittest.mock import Mock

    clock = [0.0]
    manager = FakeSessionManager(create_snapshot())
    tracker = InteractionOutcomeTracker()
    agent = QLearningAgent(seed=1)
    applier = Mock(wraps=AdaptiveActionApplier(
        parameters_manager=AdaptiveParametersManager(),
        channel_weights=AdaptiveChannelWeights(),
    ))
    controller = AdaptiveRuntimeController(
        session_manager=manager,
        action_applier=applier,
        q_agent=agent,
        interaction_outcome_tracker=tracker,
        adaptation_interval_seconds=30.0,
        min_user_events=5,
        clock=lambda: clock[0],
    )
    return controller, manager, tracker, agent, applier, clock


def test_first_window_adapts_after_five_events_and_thirty_seconds(window_runtime):
    controller, manager, tracker, _, applier, clock = window_runtime
    tracker.record_action_result(SystemAction.COPY, False)

    assert controller.step() is None
    assert controller._baseline_snapshot == manager.snapshot
    assert controller._baseline_outcome_snapshot == tracker.snapshot()
    applier.apply.assert_not_called()

    manager.snapshot = create_snapshot(duration=29.0, voice=5)
    clock[0] = 29.0
    assert controller.step() is None
    applier.apply.assert_not_called()

    manager.snapshot = create_snapshot(duration=30.0, voice=5)
    clock[0] = 30.0
    assert controller.step() is not None
    applier.apply.assert_called_once()
    assert controller._baseline_snapshot == manager.snapshot
    assert controller._baseline_outcome_snapshot == tracker.snapshot()


def test_second_window_without_activity_does_not_learn_or_apply(window_runtime):
    from unittest.mock import patch

    controller, manager, _, agent, applier, clock = window_runtime
    controller.step()
    manager.snapshot = create_snapshot(duration=30.0, voice=5)
    clock[0] = 30.0
    assert controller.step() is not None
    previous_q_table = agent.get_q_table_snapshot()
    previous_epsilon = agent.epsilon
    applier.apply.reset_mock()

    manager.snapshot = create_snapshot(duration=60.0, voice=5)
    clock[0] = 60.0
    with patch.object(agent, 'choose_action', wraps=agent.choose_action) as choose, \
         patch.object(agent, 'update', wraps=agent.update) as update, \
         patch.object(agent, 'decay_exploration', wraps=agent.decay_exploration) as decay:
        assert controller.step() is None
        # Closing the idle interval must not reuse its old activity either.
        assert controller.finalize() is None
        choose.assert_not_called()
        update.assert_not_called()
        decay.assert_not_called()
    applier.apply.assert_not_called()
    assert agent.epsilon == previous_epsilon
    assert agent.get_q_table_snapshot() == previous_q_table


def test_second_window_requires_five_new_events(window_runtime):
    from unittest.mock import patch

    controller, manager, _, agent, applier, clock = window_runtime
    controller.step()
    manager.snapshot = create_snapshot(duration=30.0, voice=5)
    clock[0] = 30.0
    assert controller.step() is not None
    previous_epsilon = agent.epsilon

    manager.snapshot = create_snapshot(duration=60.0, voice=9)
    clock[0] = 60.0
    assert controller.step() is None
    assert applier.apply.call_count == 1

    manager.snapshot = create_snapshot(duration=60.0, voice=10)
    with patch.object(agent, 'update', wraps=agent.update) as update:
        assert controller.step() is not None
        update.assert_called_once()
    assert applier.apply.call_count == 2
    assert agent.epsilon == pytest.approx(previous_epsilon * agent.epsilon_decay)
    assert controller._baseline_snapshot == manager.snapshot


def test_reward_uses_only_previous_window_metrics_and_outcomes(window_runtime):
    from unittest.mock import patch

    controller, manager, tracker, _, _, clock = window_runtime
    controller.step()
    tracker.record_action_result(SystemAction.COPY, False)
    manager.snapshot = create_snapshot(
        duration=30.0, voice=5, errors=2, switches=8,
    )
    clock[0] = 30.0
    assert controller.step() is not None

    tracker.record_action_result(SystemAction.COPY, True)
    manager.snapshot = create_snapshot(
        duration=60.0, voice=10, errors=2, switches=9,
    )
    clock[0] = 60.0
    with patch.object(
        controller.reward_calculator, 'calculate',
        wraps=controller.reward_calculator.calculate,
    ) as calculate:
        assert controller.step() is not None
        context = calculate.call_args.args[0]
        assert context.error is False
        assert context.success is True
        assert context.switch_rate == pytest.approx(2.0)
        assert context.action_failure_rate == 0.0

    tracker.record_action_result(SystemAction.COPY, False)
    manager.snapshot = create_snapshot(
        duration=90.0, voice=15, errors=3, switches=11,
    )
    clock[0] = 90.0
    with patch.object(
        controller.reward_calculator, 'calculate',
        wraps=controller.reward_calculator.calculate,
    ) as calculate:
        assert controller.step() is not None
        context = calculate.call_args.args[0]
        assert context.error is True
        assert context.success is False
        assert context.switch_rate == pytest.approx(4.0)
        assert context.action_failure_rate == 1.0
    assert controller._baseline_snapshot == manager.snapshot
    assert controller._baseline_outcome_snapshot == tracker.snapshot()


def create_observed_runtime(callback, system_mode_manager=None):
    manager = FakeSessionManager(create_snapshot())
    clock = [0.0]
    parameters = AdaptiveParametersManager()
    weights = AdaptiveChannelWeights()
    tracker = InteractionOutcomeTracker()
    agent = QLearningAgent(seed=1)
    controller = AdaptiveRuntimeController(
        session_manager=manager,
        action_applier=AdaptiveActionApplier(parameters, weights),
        q_agent=agent,
        interaction_outcome_tracker=tracker,
        min_user_events=5,
        clock=lambda: clock[0],
        on_adaptation=callback,
        system_mode_manager=system_mode_manager,
    )
    return controller, manager, clock, agent, parameters, weights, tracker


def test_valid_step_notifies_once_with_state_and_before_after_snapshots():
    notifications = []
    controller, manager, clock, agent, parameters, weights, _ = (
        create_observed_runtime(notifications.append)
    )
    assert controller.step() is None
    assert notifications == []
    manager.snapshot = create_snapshot(duration=30, head=5)
    clock[0] = 30
    state = controller.state_builder.build(manager.snapshot)
    agent.set_q_value(state, AdaptiveAction.INCREASE_HEAD_SENSITIVITY, 10)
    result = controller.step()

    assert notifications == [result]
    assert result.state_key == state.as_key()
    assert result.action == AdaptiveAction.INCREASE_HEAD_SENSITIVITY
    assert result.changed is True
    assert result.reward is None
    assert result.fatigue_score == controller.fatigue_estimator.estimate(manager.snapshot).score
    assert result.epsilon == agent.epsilon
    assert result.parameters_before.head_sensitivity_factor == 1.0
    assert result.parameters_after.head_sensitivity_factor == 1.05
    assert result.parameters_after == parameters.snapshot()
    assert result.weights_before == result.weights_after == weights.snapshot()
    assert result.action_failure_rate == 0.0
    assert result.drag_failure_rate == 0.0
    assert result.correction_rate == 0.0
    parameters.apply(AdaptiveAction.INCREASE_HEAD_SENSITIVITY)
    assert result.parameters_after.head_sensitivity_factor == 1.05


def test_idle_or_early_window_does_not_notify():
    notifications = []
    controller, manager, clock, *_ = create_observed_runtime(notifications.append)
    controller.step()
    manager.snapshot = create_snapshot(duration=29, voice=5)
    clock[0] = 29
    assert controller.step() is None
    assert notifications == []
    clock[0] = 30
    manager.snapshot = create_snapshot(duration=30, voice=5)
    assert controller.step() is not None
    clock[0] = 60
    manager.snapshot = create_snapshot(duration=60, voice=5)
    assert controller.step() is None
    assert len(notifications) == 1


def test_failing_observer_preserves_learning_and_epsilon():
    from unittest.mock import Mock

    callback = Mock(side_effect=RuntimeError('Console unavailable'))
    observed = create_observed_runtime(callback)
    control = create_observed_runtime(None)
    for runtime in (observed, control):
        runtime[0].step()
    initial_epsilon = observed[3].epsilon
    for duration, events in [(30, 5), (60, 10), (90, 15)]:
        results = []
        for controller, manager, clock, *_ in (observed, control):
            manager.snapshot = create_snapshot(duration=duration, voice=events)
            clock[0] = duration
            results.append(controller.step())
        assert results[0] == results[1]
    assert callback.call_count == 3
    assert observed[3].get_q_table_snapshot() == control[3].get_q_table_snapshot()
    assert observed[3].epsilon == control[3].epsilon < initial_epsilon
    assert observed[0].get_last_error() is None


def test_no_change_is_notified_with_unchanged_snapshots():
    notifications = []
    controller, manager, clock, agent, *_ = create_observed_runtime(notifications.append)
    agent.epsilon = 0.0
    controller.step()
    manager.snapshot = create_snapshot(duration=30, voice=5)
    clock[0] = 30
    result = controller.step()
    assert notifications == [result]
    assert result.action == AdaptiveAction.NO_CHANGE
    assert result.changed is False
    assert result.parameters_before == result.parameters_after
    assert result.weights_before == result.weights_after


def test_action_at_limit_notifies_no_actual_change():
    notifications = []
    controller, manager, clock, agent, parameters, *_ = create_observed_runtime(notifications.append)
    for _ in range(20):
        parameters.apply(AdaptiveAction.INCREASE_HEAD_SENSITIVITY)
    controller.step()
    manager.snapshot = create_snapshot(duration=30, head=5)
    clock[0] = 30
    agent.epsilon = 0.0
    agent.set_q_value(
        controller.state_builder.build(manager.snapshot),
        AdaptiveAction.INCREASE_HEAD_SENSITIVITY, 10,
    )
    result = controller.step()
    assert notifications == [result]
    assert result.action == AdaptiveAction.INCREASE_HEAD_SENSITIVITY
    assert result.changed is False
    assert result.parameters_before.head_sensitivity_factor == 1.4
    assert result.parameters_after == result.parameters_before


def test_notified_reward_and_rates_reuse_existing_reward_context():
    from unittest.mock import patch

    notifications = []
    controller, manager, clock, _, _, _, tracker = create_observed_runtime(notifications.append)
    controller.step()
    manager.snapshot = create_snapshot(duration=30, voice=5)
    clock[0] = 30
    controller.step()
    tracker.record_action_result(SystemAction.START_DRAG, False)
    manager.snapshot = create_snapshot(duration=60, voice=10)
    clock[0] = 60
    with patch.object(
        controller.reward_calculator, 'calculate',
        wraps=controller.reward_calculator.calculate,
    ) as calculate, patch.object(
        controller, '_window_outcome_rates', wraps=controller._window_outcome_rates,
    ) as rates:
        result = controller.step()
    calculate.assert_called_once()
    rates.assert_called_once()
    context = calculate.call_args.args[0]
    assert notifications[-1] is result
    assert result.reward == controller.get_last_reward()
    assert result.reward is not None
    assert result.action_failure_rate == context.action_failure_rate == 1.0
    assert result.drag_failure_rate == context.drag_failure_rate == 1.0
    assert result.correction_rate == context.correction_rate == 0.0


def test_finalize_learns_without_emitting_an_adaptation_notification():
    from unittest.mock import patch

    notifications = []
    controller, manager, clock, agent, *_ = create_observed_runtime(notifications.append)
    controller.step()
    manager.snapshot = create_snapshot(duration=30, voice=5)
    clock[0] = 30
    controller.step()
    manager.snapshot = create_snapshot(duration=60, voice=10)
    clock[0] = 60
    with patch.object(agent, 'choose_action', wraps=agent.choose_action) as choose, \
         patch.object(controller.action_applier, 'apply', wraps=controller.action_applier.apply) as apply:
        assert controller.finalize() is not None
    choose.assert_not_called()
    apply.assert_not_called()
    assert len(notifications) == 1


def test_diagnostic_snapshot_failure_does_not_block_adaptation():
    from unittest.mock import patch

    notifications = []
    controller, manager, clock, agent, parameters, *_ = create_observed_runtime(notifications.append)
    agent.epsilon = 0.0
    controller.step()
    manager.snapshot = create_snapshot(duration=30, voice=5)
    clock[0] = 30
    with patch.object(parameters, 'snapshot', side_effect=RuntimeError('Unavailable')):
        result = controller.step()
    assert notifications == [result]
    assert result.parameters_before is None
    assert result.parameters_after is None
    assert result.action == AdaptiveAction.NO_CHANGE


@pytest.fixture
def suspendable_runtime():
    from application.interaction.system_mode_manager import SystemModeManager

    state = SystemModeManager()
    notifications = []
    runtime = create_observed_runtime(notifications.append, state)
    controller, manager, clock, agent, parameters, weights, tracker = runtime
    controller.step()
    manager.snapshot = create_snapshot(duration=30, head=5)
    clock[0] = 30.0
    key = controller.state_builder.build(manager.snapshot)
    agent.set_q_value(key, AdaptiveAction.INCREASE_HEAD_SENSITIVITY, 10.0)
    first = controller.step()
    assert first.action == AdaptiveAction.INCREASE_HEAD_SENSITIVITY
    assert parameters.snapshot().head_sensitivity_factor == 1.05

    manager.snapshot = create_snapshot(duration=60, head=10)
    clock[0] = 60.0
    key = controller.state_builder.build(manager.snapshot)
    agent.set_q_value(key, AdaptiveAction.INCREASE_VOICE_WEIGHT, 20.0)
    second = controller.step()
    assert second.action == AdaptiveAction.INCREASE_VOICE_WEIGHT
    assert weights.snapshot().voice == 1.05
    assert agent.epsilon < 0.1
    # Five unconsumed events and failures accumulated BEFORE suspension.
    manager.snapshot = create_snapshot(duration=75, head=15, errors=1, switches=6)
    tracker.record_action_result(SystemAction.COPY, False)
    return runtime, state, notifications


def learned_snapshot(runtime):
    _, _, _, agent, parameters, weights, _ = runtime
    return (
        agent.get_q_table_snapshot(), agent.epsilon,
        parameters.snapshot(), weights.snapshot(),
    )


def test_suspension_freezes_learning_parameters_weights_and_notifications(suspendable_runtime):
    from unittest.mock import patch

    runtime, state, notifications = suspendable_runtime
    controller, manager, clock, agent, _, _, _ = runtime
    learned = learned_snapshot(runtime)
    notification_count = len(notifications)
    state.suspend()
    with patch.object(agent, 'choose_action', wraps=agent.choose_action) as choose, \
         patch.object(agent, 'update', wraps=agent.update) as update, \
         patch.object(agent, 'decay_exploration', wraps=agent.decay_exploration) as decay, \
         patch.object(controller.action_applier, 'apply', wraps=controller.action_applier.apply) as apply, \
         patch.object(controller.reward_calculator, 'calculate', wraps=controller.reward_calculator.calculate) as reward:
        for duration in (90, 120, 150, 180):
            clock[0] = duration
            manager.snapshot = create_snapshot(duration=duration, head=15, errors=1, switches=6)
            assert controller.step() is None
            assert controller.step(force=True) is None
            assert controller.finalize() is None
            assert learned_snapshot(runtime) == learned
            assert len(notifications) == notification_count
        choose.assert_not_called()
        update.assert_not_called()
        decay.assert_not_called()
        apply.assert_not_called()
        reward.assert_not_called()


def test_resume_rebaselines_metrics_outcomes_and_time_without_losing_learning(suspendable_runtime):
    runtime, state, notifications = suspendable_runtime
    controller, manager, clock, _, _, _, tracker = runtime
    learned = learned_snapshot(runtime)
    state.suspend()
    clock[0] = 150.0
    assert controller.step() is None
    state.activate()
    manager.snapshot = create_snapshot(duration=150, head=15, errors=1, switches=6)
    assert controller.step() is None
    assert controller._baseline_snapshot == manager.snapshot
    assert controller._baseline_outcome_snapshot == tracker.snapshot()
    assert controller._last_adaptation_time == 150.0
    assert controller._previous_state is None
    assert controller._previous_action is None
    assert learned_snapshot(runtime) == learned
    assert len(notifications) == 2

    # Even another full interval cannot recycle the five old events.
    clock[0] = 180.0
    manager.snapshot = create_snapshot(duration=180, head=15, errors=1, switches=6)
    assert controller.step() is None
    assert learned_snapshot(runtime) == learned
    assert len(notifications) == 2


def test_resume_requires_new_events_and_a_full_new_interval(suspendable_runtime):
    runtime, state, notifications = suspendable_runtime
    controller, manager, clock, agent, *_ = runtime
    state.suspend()
    clock[0] = 150.0
    state.activate()
    manager.snapshot = create_snapshot(duration=150, head=15, errors=1, switches=6)
    assert controller.step() is None
    epsilon = agent.epsilon

    # Four fresh events after a full interval are insufficient.
    manager.snapshot = create_snapshot(duration=180, head=19, errors=1, switches=6)
    clock[0] = 180.0
    assert controller.step() is None
    assert agent.epsilon == epsilon
    assert len(notifications) == 2

    # The fifth fresh event enables normal selection/application.
    manager.snapshot = create_snapshot(duration=180, head=20, errors=1, switches=6)
    result = controller.step()
    assert result is not None
    assert result.reward is None  # No credit for the pre-suspension action.
    assert result.action in agent.actions
    assert agent.epsilon == epsilon
    assert len(notifications) == 3

    # Learning and epsilon decay resume on the next fresh transition.
    manager.snapshot = create_snapshot(duration=210, head=25, errors=1, switches=6)
    clock[0] = 210.0
    result = controller.step()
    assert result is not None
    assert result.reward is not None
    assert result.action_failure_rate == 0.0  # Old outcome failure was excluded.
    assert agent.epsilon == pytest.approx(epsilon * agent.epsilon_decay)
    assert len(notifications) == 4


def test_resume_does_not_count_suspended_time_toward_next_window(suspendable_runtime):
    runtime, state, _ = suspendable_runtime
    controller, manager, clock, *_ = runtime
    state.suspend()
    clock[0] = 300.0
    state.activate()
    manager.snapshot = create_snapshot(duration=300, head=15, errors=1, switches=6)
    assert controller.step() is None
    manager.snapshot = create_snapshot(duration=329, head=20)
    clock[0] = 329.0
    assert controller.step() is None
    manager.snapshot = create_snapshot(duration=330, head=20)
    clock[0] = 330.0
    assert controller.step() is not None


def test_suspend_resume_between_worker_polls_is_detected(suspendable_runtime):
    runtime, state, notifications = suspendable_runtime
    controller, _, clock, *_ = runtime
    learned = learned_snapshot(runtime)
    # No step() sees the suspended state. Generation still records the gap.
    state.suspend()
    clock[0] = 150.0
    state.activate()
    assert controller.step(force=True) is None
    assert controller._last_adaptation_time == 150.0
    clock[0] = 180.0
    assert controller.step() is None
    assert learned_snapshot(runtime) == learned
    assert len(notifications) == 2


def test_finalize_cannot_learn_across_suspend_resume(suspendable_runtime):
    runtime, state, notifications = suspendable_runtime
    controller, _, clock, *_ = runtime
    learned = learned_snapshot(runtime)
    state.suspend()
    assert controller.finalize() is None
    clock[0] = 150.0
    state.activate()
    # Shutdown before the first active worker tick must also rebaseline.
    assert controller.finalize() is None
    assert learned_snapshot(runtime) == learned
    assert len(notifications) == 2


def test_runtime_started_suspended_keeps_thread_alive_without_learning():
    from application.interaction.system_mode_manager import SystemModeManager

    state = SystemModeManager()
    state.suspend()
    runtime = create_observed_runtime(None, state)
    controller, manager, clock, *_ = runtime
    manager.snapshot = create_snapshot(duration=30, head=5)
    clock[0] = 30.0
    learned = learned_snapshot(runtime)
    try:
        assert controller.start() is True
        assert controller.is_running
        assert controller.step() is None
        assert learned_snapshot(runtime) == learned
    finally:
        controller.stop()
    assert not controller.is_running
    assert learned_snapshot(runtime) == learned


def test_suspension_waits_for_learning_and_callback_in_progress(suspendable_runtime):
    import threading

    runtime, state, notifications = suspendable_runtime
    controller, manager, clock, *_ = runtime
    entered, release, requested, suspended = (threading.Event() for _ in range(4))
    errors = []

    def callback(result):
        entered.set()
        if not release.wait(3):
            errors.append('Callback was not released')
        assert not state.is_suspended()
        notifications.append(result)

    def suspend():
        requested.set()
        state.suspend()
        suspended.set()

    controller.on_adaptation = callback
    manager.snapshot = create_snapshot(duration=90, head=15)
    clock[0] = 90.0
    worker = threading.Thread(target=controller.step, daemon=True)
    suspender = threading.Thread(target=suspend, daemon=True)
    worker.start()
    try:
        assert entered.wait(3)
        suspender.start()
        assert requested.wait(3)
        assert not suspended.is_set()
    finally:
        release.set()
        worker.join(3)
        if suspender.ident is not None:
            suspender.join(3)
    assert not worker.is_alive() and not suspender.is_alive()
    assert not errors
    assert suspended.is_set()
    assert len(notifications) == 3
    learned = learned_snapshot(runtime)
    count = len(notifications)
    clock[0] = 180.0
    assert controller.step() is None
    assert learned_snapshot(runtime) == learned
    assert len(notifications) == count
