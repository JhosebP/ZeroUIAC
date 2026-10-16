import random
import threading

from modules.adaptation.adaptive_actions import (
    AdaptiveAction,
)


class QLearningAgent:
    """
    Agente Q-learning tabular para ZeroUI-AC.

    Aprende qué acción adaptativa conviene
    aplicar en cada estado discreto.

    No ejecuta acciones sobre Windows.
    """

    def __init__(
        self,
        learning_rate=0.20,
        discount_factor=0.90,
        epsilon=0.10,
        epsilon_min=0.02,
        epsilon_decay=0.995,
        seed=None,
    ):

        self._validate_probability(
            learning_rate,
            "learning_rate",
        )

        self._validate_probability(
            discount_factor,
            "discount_factor",
        )

        self._validate_probability(
            epsilon,
            "epsilon",
        )

        self._validate_probability(
            epsilon_min,
            "epsilon_min",
        )

        if epsilon_min > epsilon:
            raise ValueError(
                "epsilon_min no puede ser "
                "mayor que epsilon."
            )

        if not (
            0.0
            < epsilon_decay
            <= 1.0
        ):
            raise ValueError(
                "epsilon_decay debe estar "
                "entre 0 y 1."
            )

        self.learning_rate = (
            float(learning_rate)
        )

        self.discount_factor = (
            float(discount_factor)
        )

        self.epsilon = (
            float(epsilon)
        )

        self.epsilon_min = (
            float(epsilon_min)
        )

        self.epsilon_decay = (
            float(epsilon_decay)
        )

        self.actions = tuple(
            AdaptiveAction
        )

        self._q_table = {}

        self._lock = (
            threading.RLock()
        )

        self._random = (
            random.Random(seed)
        )

    def _validate_probability(
        self,
        value,
        name,
    ):

        if not (
            0.0
            <= float(value)
            <= 1.0
        ):

            raise ValueError(
                f"{name} debe estar "
                "entre 0 y 1."
            )

    def _state_key(
        self,
        state,
    ):
        """
        Convierte AdaptiveState o una tupla
        en una clave estable para la Q-table.
        """

        if state is None:
            raise ValueError(
                "El estado no puede ser None."
            )

        if hasattr(
            state,
            "as_key",
        ):

            key = (
                state.as_key()
            )

        else:

            key = state

        if not isinstance(
            key,
            tuple,
        ):

            raise ValueError(
                "El estado debe producir "
                "una clave tipo tuple."
            )

        return key

    def _ensure_state(
        self,
        state_key,
    ):

        if (
            state_key
            not in self._q_table
        ):

            self._q_table[
                state_key
            ] = {
                action: 0.0
                for action
                in self.actions
            }

    def get_q_value(
        self,
        state,
        action,
    ):

        if not isinstance(
            action,
            AdaptiveAction,
        ):

            raise ValueError(
                "Acción adaptativa inválida."
            )

        state_key = (
            self._state_key(
                state
            )
        )

        with self._lock:

            self._ensure_state(
                state_key
            )

            return (
                self._q_table[
                    state_key
                ][action]
            )

    def set_q_value(
        self,
        state,
        action,
        value,
    ):
        """
        Método útil para pruebas,
        restauración futura y depuración.
        """

        if not isinstance(
            action,
            AdaptiveAction,
        ):

            raise ValueError(
                "Acción adaptativa inválida."
            )

        state_key = (
            self._state_key(
                state
            )
        )

        with self._lock:

            self._ensure_state(
                state_key
            )

            self._q_table[
                state_key
            ][action] = float(
                value
            )

    def choose_action(
        self,
        state,
    ):
        """
        Selección epsilon-greedy.

        epsilon:
            explora una acción aleatoria.

        1 - epsilon:
            utiliza la acción con mayor
            valor aprendido.
        """

        state_key = (
            self._state_key(
                state
            )
        )

        with self._lock:

            self._ensure_state(
                state_key
            )

            if (
                self._random.random()
                < self.epsilon
            ):

                return (
                    self._random.choice(
                        self.actions
                    )
                )

            values = (
                self._q_table[
                    state_key
                ]
            )

            best_value = max(
                values.values()
            )

            best_actions = [
                action
                for action, value
                in values.items()
                if value == best_value
            ]

            return (
                self._random.choice(
                    best_actions
                )
            )

    def update(
        self,
        state,
        action,
        reward,
        next_state,
        terminal=False,
    ):
        """
        Aplica la ecuación clásica:

        Q(s,a) =
            Q(s,a)
            + alpha *
            [reward
             + gamma * max Q(s',a')
             - Q(s,a)]
        """

        if not isinstance(
            action,
            AdaptiveAction,
        ):

            raise ValueError(
                "Acción adaptativa inválida."
            )

        state_key = (
            self._state_key(
                state
            )
        )

        next_state_key = (
            self._state_key(
                next_state
            )
        )

        reward = float(
            reward
        )

        with self._lock:

            self._ensure_state(
                state_key
            )

            self._ensure_state(
                next_state_key
            )

            current_q = (
                self._q_table[
                    state_key
                ][action]
            )

            if terminal:

                future_q = 0.0

            else:

                future_q = max(
                    self._q_table[
                        next_state_key
                    ].values()
                )

            target = (
                reward
                + self.discount_factor
                * future_q
            )

            new_q = (
                current_q
                + self.learning_rate
                * (
                    target
                    - current_q
                )
            )

            self._q_table[
                state_key
            ][action] = (
                new_q
            )

            return new_q

    def decay_exploration(self):
        """
        Reduce gradualmente epsilon sin
        bajar del mínimo configurado.
        """

        with self._lock:

            self.epsilon = max(
                self.epsilon_min,
                self.epsilon
                * self.epsilon_decay,
            )

            return self.epsilon

    def get_state_values(
        self,
        state,
    ):
        """
        Devuelve una copia de los valores
        Q de un estado.
        """

        state_key = (
            self._state_key(
                state
            )
        )

        with self._lock:

            self._ensure_state(
                state_key
            )

            return dict(
                self._q_table[
                    state_key
                ]
            )

    def get_q_table_snapshot(
        self,
    ):
        """
        Devuelve una copia estable
        de toda la tabla Q.
        """

        with self._lock:

            return {
                state: dict(values)
                for state, values
                in self._q_table.items()
            }