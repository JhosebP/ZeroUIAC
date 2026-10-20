import threading
import time

from dataclasses import dataclass

from modules.adaptation.adaptive_state import (
    AdaptiveStateBuilder
)

from modules.adaptation.q_learning_agent import (
    QLearningAgent
)

from modules.adaptation.reward_function import (
    RewardCalculator,
    RewardContext
)

from modules.adaptation.fatigue_estimator import (
    FatigueEstimator
)


@dataclass(frozen=True)
class AdaptationStepResult:

    action: object
    changed: bool

    reward: object

    fatigue_score: float

    state_key: tuple


class AdaptiveRuntimeController:
    """
    Coordina el aprendizaje adaptativo
    durante una sesión.

    Nunca ejecuta acciones sobre Windows.

    La adaptación se realiza por ventanas
    temporales y no por frame de cámara.
    """

    USER_SOURCE_KEYS = (
        "voice",
        "head",
        "limb",
        "gesture",
    )

    def __init__(
        self,
        session_manager,
        action_applier,
        state_builder=None,
        q_agent=None,
        reward_calculator=None,
        fatigue_estimator=None,
        adaptation_interval_seconds=30.0,
        worker_poll_seconds=1.0,
        min_user_events=1,
        clock=None,
    ):

        if adaptation_interval_seconds < 0:

            raise ValueError(
                "El intervalo adaptativo "
                "no puede ser negativo."
            )

        if worker_poll_seconds <= 0:

            raise ValueError(
                "El intervalo de consulta "
                "debe ser mayor que cero."
            )

        if min_user_events < 1:

            raise ValueError(
                "min_user_events debe ser "
                "al menos 1."
            )

        self.session_manager = (
            session_manager
        )

        self.action_applier = (
            action_applier
        )

        self.state_builder = (
            state_builder
            or AdaptiveStateBuilder()
        )

        self.q_agent = (
            q_agent
            or QLearningAgent()
        )

        self.reward_calculator = (
            reward_calculator
            or RewardCalculator()
        )

        self.fatigue_estimator = (
            fatigue_estimator
            or FatigueEstimator()
        )

        self.adaptation_interval_seconds = (
            float(
                adaptation_interval_seconds
            )
        )

        self.worker_poll_seconds = (
            float(
                worker_poll_seconds
            )
        )

        self.min_user_events = int(
            min_user_events
        )

        self._clock = (
            clock
            or time.monotonic
        )

        self._lock = (
            threading.RLock()
        )

        self._stop_event = (
            threading.Event()
        )

        self._thread = None

        self._running = False

        self._baseline_snapshot = None

        self._previous_state = None
        self._previous_action = None

        self._last_adaptation_time = None

        self._last_reward = None
        self._last_error = None

    @property
    def is_running(self):

        with self._lock:

            return self._running

    def _metrics(
        self,
        snapshot
    ):

        if not snapshot:
            return {}

        return (
            snapshot.get(
                "metrics",
                snapshot
            )
            or {}
        )

    def _user_event_count(
        self,
        snapshot
    ):

        metrics = self._metrics(
            snapshot
        )

        source_counts = (
            metrics.get(
                "source_counts",
                {}
            )
            or {}
        )

        return sum(
            max(
                0,
                int(
                    source_counts.get(
                        source,
                        0
                    )
                    or 0
                )
            )
            for source
            in self.USER_SOURCE_KEYS
        )

    def _user_event_delta(
        self,
        previous_snapshot,
        current_snapshot
    ):

        return max(
            0,
            self._user_event_count(
                current_snapshot
            )
            - self._user_event_count(
                previous_snapshot
            )
        )

    @staticmethod
    def _safe_number(
        value,
        default=0.0
    ):

        try:

            return float(
                value
            )

        except (
            TypeError,
            ValueError
        ):

            return default

    def _window_action_interval(
        self,
        previous_metrics,
        current_metrics
    ):

        previous_samples = max(
            0,
            int(
                self._safe_number(
                    previous_metrics.get(
                        "action_interval_samples",
                        0
                    )
                )
            )
        )

        current_samples = max(
            0,
            int(
                self._safe_number(
                    current_metrics.get(
                        "action_interval_samples",
                        0
                    )
                )
            )
        )

        sample_delta = max(
            0,
            current_samples
            - previous_samples
        )

        if sample_delta == 0:
            return 0.0

        previous_average = max(
            0.0,
            self._safe_number(
                previous_metrics.get(
                    "average_action_interval_seconds",
                    0.0
                )
            )
        )

        current_average = max(
            0.0,
            self._safe_number(
                current_metrics.get(
                    "average_action_interval_seconds",
                    0.0
                )
            )
        )

        previous_total = (
            previous_average
            * previous_samples
        )

        current_total = (
            current_average
            * current_samples
        )

        interval_total = max(
            0.0,
            current_total
            - previous_total
        )

        return (
            interval_total
            / sample_delta
        )

    def _build_reward_context(
        self,
        previous_snapshot,
        current_snapshot
    ):

        previous_metrics = (
            self._metrics(
                previous_snapshot
            )
        )

        current_metrics = (
            self._metrics(
                current_snapshot
            )
        )

        previous_errors = max(
            0,
            int(
                self._safe_number(
                    previous_metrics.get(
                        "voice_error_events",
                        0
                    )
                )
            )
        )

        current_errors = max(
            0,
            int(
                self._safe_number(
                    current_metrics.get(
                        "voice_error_events",
                        0
                    )
                )
            )
        )

        error_delta = max(
            0,
            current_errors
            - previous_errors
        )

        previous_switches = max(
            0,
            int(
                self._safe_number(
                    previous_metrics.get(
                        "user_channel_switches",
                        0
                    )
                )
            )
        )

        current_switches = max(
            0,
            int(
                self._safe_number(
                    current_metrics.get(
                        "user_channel_switches",
                        0
                    )
                )
            )
        )

        switch_delta = max(
            0,
            current_switches
            - previous_switches
        )

        previous_duration = max(
            0.0,
            self._safe_number(
                previous_metrics.get(
                    "duration_seconds",
                    0.0
                )
            )
        )

        current_duration = max(
            0.0,
            self._safe_number(
                current_metrics.get(
                    "duration_seconds",
                    0.0
                )
            )
        )

        duration_delta = max(
            0.0,
            current_duration
            - previous_duration
        )

        if duration_delta > 0.0:

            switch_rate = (
                switch_delta
                * 60.0
                / duration_delta
            )

        else:

            switch_rate = 0.0

        latency = (
            self._window_action_interval(
                previous_metrics,
                current_metrics
            )
        )

        fatigue = (
            self.fatigue_estimator
            .estimate(
                current_snapshot
            )
        )

        has_activity = (
            self._user_event_delta(
                previous_snapshot,
                current_snapshot
            )
            > 0
        )

        return RewardContext(
            success=(
                has_activity
                and error_delta == 0
            ),

            error=(
                error_delta > 0
            ),

            latency_seconds=(
                latency
            ),

            switch_rate=(
                switch_rate
            ),

            fatigue_level=(
                fatigue.score
            ),
        )

    def step(
        self,
        force=False
    ):
        """
        Ejecuta como máximo un ciclo
        de adaptación.
        """

        snapshot = (
            self.session_manager
            .get_snapshot()
        )

        if snapshot is None:
            return None

        now = self._clock()

        with self._lock:

            if (
                self._baseline_snapshot
                is None
            ):

                self._baseline_snapshot = (
                    snapshot
                )

                self._last_adaptation_time = (
                    now
                )

                return None

            if (
                not force
                and self._last_adaptation_time
                is not None
                and now
                - self._last_adaptation_time
                < self.adaptation_interval_seconds
            ):

                return None

            user_event_delta = (
                self._user_event_delta(
                    self._baseline_snapshot,
                    snapshot
                )
            )

            if (
                user_event_delta
                < self.min_user_events
            ):

                return None

            current_state = (
                self.state_builder
                .build(
                    snapshot
                )
            )

            fatigue = (
                self.fatigue_estimator
                .estimate(
                    snapshot
                )
            )

            reward = None

            if (
                self._previous_state
                is not None
                and self._previous_action
                is not None
            ):

                context = (
                    self._build_reward_context(
                        self._baseline_snapshot,
                        snapshot
                    )
                )

                reward = (
                    self.reward_calculator
                    .calculate(
                        context
                    )
                )

                self.q_agent.update(
                    state=(
                        self._previous_state
                    ),
                    action=(
                        self._previous_action
                    ),
                    reward=reward,
                    next_state=current_state,
                    terminal=False,
                )

                self.q_agent \
                    .decay_exploration()

            action = (
                self.q_agent
                .choose_action(
                    current_state
                )
            )

            changed = (
                self.action_applier
                .apply(
                    action
                )
            )

            self._previous_state = (
                current_state
            )

            self._previous_action = (
                action
            )

            self._baseline_snapshot = (
                snapshot
            )

            self._last_adaptation_time = (
                now
            )

            self._last_reward = (
                reward
            )

            return AdaptationStepResult(
                action=action,
                changed=changed,
                reward=reward,
                fatigue_score=(
                    fatigue.score
                ),
                state_key=(
                    current_state.as_key()
                ),
            )

    def finalize(self):
        """
        Aprende del último intervalo sin
        aplicar una nueva modificación.
        """

        snapshot = (
            self.session_manager
            .get_snapshot()
        )

        if snapshot is None:
            return None

        with self._lock:

            if (
                self._baseline_snapshot
                is None
                or self._previous_state
                is None
                or self._previous_action
                is None
            ):

                return None

            if (
                self._user_event_delta(
                    self._baseline_snapshot,
                    snapshot
                )
                < self.min_user_events
            ):

                return None

            current_state = (
                self.state_builder
                .build(
                    snapshot
                )
            )

            context = (
                self._build_reward_context(
                    self._baseline_snapshot,
                    snapshot
                )
            )

            reward = (
                self.reward_calculator
                .calculate(
                    context
                )
            )

            self.q_agent.update(
                state=self._previous_state,
                action=self._previous_action,
                reward=reward,
                next_state=current_state,
                terminal=True,
            )

            self.q_agent \
                .decay_exploration()

            self._baseline_snapshot = (
                snapshot
            )

            self._previous_state = None
            self._previous_action = None

            self._last_reward = reward

            return reward

    def _run(self):

        while not self._stop_event.wait(
            self.worker_poll_seconds
        ):

            try:

                self.step()

            except Exception as error:

                with self._lock:

                    self._last_error = (
                        f"{type(error).__name__}: "
                        f"{error}"
                    )

    def start(self):

        snapshot = (
            self.session_manager
            .get_snapshot()
        )

        if snapshot is None:
            return False

        with self._lock:

            if self._running:
                return False

            self._baseline_snapshot = (
                snapshot
            )

            self._previous_state = None
            self._previous_action = None

            self._last_adaptation_time = (
                self._clock()
            )

            self._last_reward = None
            self._last_error = None

            self._stop_event.clear()

            self._thread = (
                threading.Thread(
                    target=self._run,
                    daemon=True,
                    name=(
                        "ZeroUIAdaptiveRuntime"
                    ),
                )
            )

            self._running = True

            self._thread.start()

            return True

    def stop(self):

        with self._lock:

            if not self._running:
                return False

            thread = self._thread

            self._stop_event.set()

        if thread is not None:

            thread.join(
                timeout=(
                    self.worker_poll_seconds
                    + 1.0
                )
            )

        try:

            self.finalize()

        except Exception as error:

            with self._lock:

                self._last_error = (
                    f"{type(error).__name__}: "
                    f"{error}"
                )

        with self._lock:

            self._running = False
            self._thread = None

        return True

    def get_last_error(self):

        with self._lock:

            return self._last_error

    def get_last_reward(self):

        with self._lock:

            return self._last_reward