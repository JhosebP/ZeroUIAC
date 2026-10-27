import json
import threading

from pathlib import Path

from modules.adaptation.adaptive_actions import (
    AdaptiveAction
)


class QLearningPersistence:
    """
    Guarda y recupera el aprendizaje
    del agente Q-learning.

    No ejecuta acciones sobre Windows.
    """

    SCHEMA_VERSION = 1

    def __init__(
        self,
        file_path=None
    ):

        if file_path is None:

            file_path = (
                Path("data")
                / "adaptation"
                / "q_learning.json"
            )

        self.file_path = Path(
            file_path
        )

        self._lock = (
            threading.RLock()
        )

    def save(
        self,
        agent
    ):
        """
        Guarda tabla Q y nivel actual
        de exploración epsilon.
        """

        if agent is None:

            raise ValueError(
                "El agente no puede ser None."
            )

        snapshot = (
            agent.get_q_table_snapshot()
        )

        q_table = []

        for state, values in (
            snapshot.items()
        ):

            q_table.append(
                {
                    "state": list(state),

                    "values": {
                        action.value:
                            float(value)

                        for action, value
                        in values.items()
                    }
                }
            )

        data = {
            "schema_version":
                self.SCHEMA_VERSION,

            "epsilon":
                float(agent.epsilon),

            "q_table":
                q_table,
        }

        with self._lock:

            self.file_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            temporary_path = (
                self.file_path
                .with_suffix(
                    self.file_path.suffix
                    + ".tmp"
                )
            )

            temporary_path.write_text(
                json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=2
                ),
                encoding="utf-8"
            )

            temporary_path.replace(
                self.file_path
            )

        return True

    def load(
        self,
        agent
    ):
        """
        Restaura tabla Q y epsilon.

        Retorna False cuando todavía
        no existe aprendizaje guardado.
        """

        if agent is None:

            raise ValueError(
                "El agente no puede ser None."
            )

        with self._lock:

            if not self.file_path.exists():

                return False

            try:

                data = json.loads(
                    self.file_path.read_text(
                        encoding="utf-8"
                    )
                )

            except (
                OSError,
                json.JSONDecodeError
            ) as error:

                raise ValueError(
                    "No se pudo leer "
                    "el aprendizaje guardado."
                ) from error

        if (
            data.get(
                "schema_version"
            )
            != self.SCHEMA_VERSION
        ):

            raise ValueError(
                "Versión de aprendizaje "
                "no compatible."
            )

        q_table = data.get(
            "q_table",
            []
        )

        if not isinstance(
            q_table,
            list
        ):

            raise ValueError(
                "Tabla Q guardada inválida."
            )

        for entry in q_table:

            if not isinstance(
                entry,
                dict
            ):

                raise ValueError(
                    "Estado Q inválido."
                )

            state_data = entry.get(
                "state"
            )

            values = entry.get(
                "values"
            )

            if (
                not isinstance(
                    state_data,
                    list
                )
                or not isinstance(
                    values,
                    dict
                )
            ):

                raise ValueError(
                    "Entrada de tabla Q "
                    "inválida."
                )

            state = tuple(
                state_data
            )

            for (
                action_name,
                value
            ) in values.items():

                try:

                    action = (
                        AdaptiveAction(
                            action_name
                        )
                    )

                    numeric_value = float(
                        value
                    )

                except (
                    ValueError,
                    TypeError
                ) as error:

                    raise ValueError(
                        "Valor de tabla Q "
                        "inválido."
                    ) from error

                agent.set_q_value(
                    state,
                    action,
                    numeric_value
                )

        epsilon = data.get(
            "epsilon"
        )

        if epsilon is not None:

            try:

                epsilon = float(
                    epsilon
                )

            except (
                TypeError,
                ValueError
            ) as error:

                raise ValueError(
                    "Epsilon guardado "
                    "inválido."
                ) from error

            agent.epsilon = max(
                agent.epsilon_min,
                min(
                    1.0,
                    epsilon
                )
            )

        return True