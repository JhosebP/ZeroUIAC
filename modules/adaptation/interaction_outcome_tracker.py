import math
import threading

from domain.commands.system_actions import (
    SystemAction
)

from domain.events.event_types import (
    EventType
)


class InteractionOutcomeTracker:
    """
    Registra resultados técnicos de las
    interacciones del usuario.

    No controla Windows.
    No modifica parámetros adaptativos.
    No ejecuta Q-learning.
    """

    INTERRUPTING_ACTIONS = {
        SystemAction.LEFT_CLICK,
        SystemAction.RIGHT_CLICK,
        SystemAction.DOUBLE_CLICK,
    }

    def __init__(self):

        self._lock = (
            threading.RLock()
        )

        self.action_attempts = 0
        self.action_successes = 0
        self.action_failures = 0

        self.drag_attempts = 0
        self.drag_successes = 0
        self.drag_failures = 0

        self.cursor_samples = 0
        self.correction_events = 0

        self._drag_active = False
        self._drag_had_movement = False

        self._last_vector_by_source = {}

        self._last_absolute_position = {}

    def _safe_float(
        self,
        value
    ):

        try:

            value = float(
                value
            )

        except (
            TypeError,
            ValueError
        ):

            return None

        if not math.isfinite(
            value
        ):

            return None

        return value

    def _register_vector(
        self,
        source,
        dx,
        dy
    ):
        """
        Registra un vector de movimiento.

        Se considera corrección fuerte cuando
        el nuevo vector forma un ángulo mayor
        de 90 grados con el anterior.
        """

        magnitude = math.hypot(
            dx,
            dy
        )

        if magnitude <= 0.0:
            return False

        self.cursor_samples += 1

        previous = (
            self._last_vector_by_source
            .get(
                source
            )
        )

        corrected = False

        if previous is not None:

            previous_dx, previous_dy = (
                previous
            )

            dot_product = (
                previous_dx * dx
                + previous_dy * dy
            )

            if dot_product < 0.0:

                self.correction_events += 1

                corrected = True

        self._last_vector_by_source[
            source
        ] = (
            dx,
            dy
        )

        if self._drag_active:

            self._drag_had_movement = True

        return corrected

    def record_cursor_event(
        self,
        event
    ):
        """
        Registra movimiento relativo o
        absoluto proveniente de un
        InteractionEvent.
        """

        if event is None:
            return False

        if (
            event.event_type
            != EventType.CURSOR_MOVE
        ):

            return False

        payload = (
            event.payload
            or {}
        )

        mode = payload.get(
            "mode"
        )

        with self._lock:

            if mode == "relative":

                dx = self._safe_float(
                    payload.get(
                        "dx",
                        0.0
                    )
                )

                dy = self._safe_float(
                    payload.get(
                        "dy",
                        0.0
                    )
                )

                if (
                    dx is None
                    or dy is None
                ):

                    return False

                return self._register_vector(
                    event.source,
                    dx,
                    dy
                )

            if mode == "absolute":

                x = self._safe_float(
                    payload.get(
                        "x"
                    )
                )

                y = self._safe_float(
                    payload.get(
                        "y"
                    )
                )

                if (
                    x is None
                    or y is None
                ):

                    return False

                previous = (
                    self._last_absolute_position
                    .get(
                        event.source
                    )
                )

                self._last_absolute_position[
                    event.source
                ] = (
                    x,
                    y
                )

                if previous is None:

                    return False

                previous_x, previous_y = (
                    previous
                )

                return self._register_vector(
                    event.source,
                    x - previous_x,
                    y - previous_y
                )

        return False

    def record_action_result(
        self,
        action,
        success
    ):
        """
        Registra si una acción técnica pudo
        ejecutarse correctamente.
        """

        if not isinstance(
            action,
            SystemAction
        ):

            return False

        success = bool(
            success
        )

        with self._lock:

            self.action_attempts += 1

            if success:

                self.action_successes += 1

            else:

                self.action_failures += 1

            # --------------------------
            # Inicio de arrastre
            # --------------------------

            if (
                action
                == SystemAction.START_DRAG
            ):

                self.drag_attempts += 1

                if success:

                    self._drag_active = True

                    self._drag_had_movement = (
                        False
                    )

                else:

                    self.drag_failures += 1

                return success

            # --------------------------
            # Fin de arrastre
            # --------------------------

            if (
                action
                == SystemAction.STOP_DRAG
            ):

                if not success:

                    self.drag_failures += 1

                    return False

                if not self._drag_active:

                    self.drag_failures += 1

                    return False

                if self._drag_had_movement:

                    self.drag_successes += 1

                else:

                    # Se presionó y soltó,
                    # pero no existió realmente
                    # desplazamiento.
                    self.drag_failures += 1

                self._drag_active = False

                self._drag_had_movement = (
                    False
                )

                return True

            # --------------------------
            # Un clic mientras existe
            # un arrastre lo interrumpe.
            # --------------------------

            if (
                action
                in self.INTERRUPTING_ACTIONS
                and self._drag_active
            ):

                self.drag_failures += 1

                self._drag_active = False

                self._drag_had_movement = (
                    False
                )

            return success

    def finalize_pending_drag(
        self
    ):
        """
        Marca como fallido un arrastre que
        quedó abierto al finalizar sesión.
        """

        with self._lock:

            if not self._drag_active:
                return False

            self.drag_failures += 1

            self._drag_active = False

            self._drag_had_movement = False

            return True

    def get_action_success_rate(
        self
    ):

        with self._lock:

            if self.action_attempts == 0:
                return 0.0

            return (
                self.action_successes
                / self.action_attempts
            )

    def get_drag_success_rate(
        self
    ):

        with self._lock:

            completed = (
                self.drag_successes
                + self.drag_failures
            )

            if completed == 0:
                return 0.0

            return (
                self.drag_successes
                / completed
            )

    def get_correction_rate(
        self
    ):

        with self._lock:

            if self.cursor_samples == 0:
                return 0.0

            return (
                self.correction_events
                / self.cursor_samples
            )

    def snapshot(
        self
    ):
        """
        Devuelve una copia estable de
        los resultados acumulados.
        """

        with self._lock:

            return {
                "action_attempts":
                    self.action_attempts,

                "action_successes":
                    self.action_successes,

                "action_failures":
                    self.action_failures,

                "action_success_rate":
                    self.get_action_success_rate(),

                "drag_attempts":
                    self.drag_attempts,

                "drag_successes":
                    self.drag_successes,

                "drag_failures":
                    self.drag_failures,

                "drag_success_rate":
                    self.get_drag_success_rate(),

                "drag_active":
                    self._drag_active,

                "cursor_samples":
                    self.cursor_samples,

                "correction_events":
                    self.correction_events,

                "correction_rate":
                    self.get_correction_rate(),
            }