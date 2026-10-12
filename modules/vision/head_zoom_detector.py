import time

from domain.commands.system_actions import (
    SystemAction
)


class HeadZoomDetector:
    """
    Detecta inclinaciones deliberadas de cabeza
    para controlar el zoom.

    Adelante:
    ZOOM_IN

    Atrás:
    ZOOM_OUT
    """

    def __init__(
        self,
        threshold=12.0,
        release_threshold=4.0,
        stable_frames=8,
        cooldown=0.8
    ):

        self.threshold = threshold

        self.release_threshold = (
            release_threshold
        )

        self.stable_frames = (
            stable_frames
        )

        self.cooldown = cooldown

        self._candidate = None

        self._stable_count = 0

        self._latched = False

        self._last_trigger = 0.0

    def detect(
        self,
        pitch,
        neutral_pitch
    ):

        relative_pitch = (
            pitch
            - neutral_pitch
        )

        if self._latched:

            if (
                abs(relative_pitch)
                <= self.release_threshold
            ):

                self._latched = False

                self._candidate = None

                self._stable_count = 0

            return None

        action = None

        if (
            relative_pitch
            >= self.threshold
        ):

            action = (
                SystemAction.ZOOM_IN
            )

        elif (
            relative_pitch
            <= -self.threshold
        ):

            action = (
                SystemAction.ZOOM_OUT
            )

        if action is None:

            self._candidate = None

            self._stable_count = 0

            return None

        if (
            action
            != self._candidate
        ):

            self._candidate = action

            self._stable_count = 1

        else:

            self._stable_count += 1

        if (
            self._stable_count
            < self.stable_frames
        ):

            return None

        current_time = (
            time.monotonic()
        )

        if (
            current_time
            - self._last_trigger
            < self.cooldown
        ):

            return None

        self._last_trigger = (
            current_time
        )

        self._latched = True

        self._candidate = None

        self._stable_count = 0

        return action

    @property
    def is_active(self):
    
        return (
            self._candidate is not None
            or self._latched
        )

    def reset(self):

        self._candidate = None

        self._stable_count = 0

        self._latched = False