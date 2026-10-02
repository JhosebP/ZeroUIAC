import math
import time


class GestureDetector:
    """
    Detecta gestos rápidos de la mano
    mediante landmarks de MediaPipe.

    Gestos actuales:

    - DRAW:
      índice y medio extendidos.

    - ERASE:
      índice, medio y anular extendidos.

    El gesto debe mantenerse varios
    frames para evitar falsos positivos.
    """

    GESTURE_DRAW = "draw"
    GESTURE_ERASE = "erase"

    WRIST = 0

    INDEX_PIP = 6
    INDEX_TIP = 8

    MIDDLE_PIP = 10
    MIDDLE_TIP = 12

    RING_PIP = 14
    RING_TIP = 16

    PINKY_PIP = 18
    PINKY_TIP = 20

    def __init__(
        self,
        stable_frames=5,
        extension_ratio=1.15,
        cooldown=1.0
    ):
        self.stable_frames = (
            stable_frames
        )

        self.extension_ratio = (
            extension_ratio
        )

        self.cooldown = cooldown

        self._candidate = None

        self._candidate_frames = 0

        self._latched_gesture = None

        self._last_trigger_time = 0.0

    def _distance(
        self,
        point_a,
        point_b
    ):
        return math.sqrt(
            (
                point_a.x
                - point_b.x
            ) ** 2
            + (
                point_a.y
                - point_b.y
            ) ** 2
            + (
                point_a.z
                - point_b.z
            ) ** 2
        )

    def _is_extended(
        self,
        landmarks,
        pip_index,
        tip_index
    ):
        wrist = landmarks[
            self.WRIST
        ]

        pip = landmarks[
            pip_index
        ]

        tip = landmarks[
            tip_index
        ]

        wrist_to_pip = (
            self._distance(
                wrist,
                pip
            )
        )

        wrist_to_tip = (
            self._distance(
                wrist,
                tip
            )
        )

        if wrist_to_pip <= 0:
            return False

        return (
            wrist_to_tip
            > wrist_to_pip
            * self.extension_ratio
        )

    def _classify(
        self,
        hand_landmarks
    ):
        if hand_landmarks is None:
            return None

        landmarks = (
            hand_landmarks.landmark
        )

        index_extended = (
            self._is_extended(
                landmarks,
                self.INDEX_PIP,
                self.INDEX_TIP
            )
        )

        middle_extended = (
            self._is_extended(
                landmarks,
                self.MIDDLE_PIP,
                self.MIDDLE_TIP
            )
        )

        ring_extended = (
            self._is_extended(
                landmarks,
                self.RING_PIP,
                self.RING_TIP
            )
        )

        pinky_extended = (
            self._is_extended(
                landmarks,
                self.PINKY_PIP,
                self.PINKY_TIP
            )
        )

        if (
            index_extended
            and middle_extended
            and not ring_extended
            and not pinky_extended
        ):
            return (
                self.GESTURE_DRAW
            )

        if (
            index_extended
            and middle_extended
            and ring_extended
            and not pinky_extended
        ):
            return (
                self.GESTURE_ERASE
            )

        return None

    def detect(
        self,
        hand_landmarks
    ):
        """
        Retorna el gesto solamente cuando
        ha sido estable durante varios frames.

        Mientras el usuario mantenga el mismo
        gesto no vuelve a dispararse.
        """

        gesture = (
            self._classify(
                hand_landmarks
            )
        )

        if gesture is None:

            self._candidate = None

            self._candidate_frames = 0

            self._latched_gesture = None

            return None

        if (
            gesture
            == self._latched_gesture
        ):
            return None

        if gesture != self._candidate:

            self._candidate = gesture

            self._candidate_frames = 1

            return None

        self._candidate_frames += 1

        if (
            self._candidate_frames
            < self.stable_frames
        ):
            return None

        current_time = (
            time.monotonic()
        )

        if (
            current_time
            - self._last_trigger_time
            < self.cooldown
        ):
            return None

        self._last_trigger_time = (
            current_time
        )

        self._latched_gesture = (
            gesture
        )

        self._candidate = None

        self._candidate_frames = 0

        return gesture

    def reset(self):

        self._candidate = None

        self._candidate_frames = 0

        self._latched_gesture = None