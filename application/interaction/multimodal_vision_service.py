import time
from collections import deque

import cv2

from domain.events.event_types import (
    EventSource,
    EventType
)

from domain.events.interaction_event import (
    InteractionEvent
)

from modules.vision.face_tracker import (
    FaceTracker
)

from modules.vision.head_pose import (
    HeadPoseEstimator
)

from modules.vision.head_cursor_mapper import (
    HeadCursorMapper
)

from modules.vision.head_zoom_detector import (
    HeadZoomDetector
)

from modules.vision.hand_tracker import (
    HandTracker
)

from modules.vision.limb_cursor_mapper import (
    LimbCursorMapper
)

from domain.commands.system_actions import (
    SystemAction
)

from modules.vision.gesture_detector import (
    GestureDetector
)

from application.interaction.zoom_mode_manager import (
    ZoomModeManager
)

class MultimodalVisionService:
    """
    Procesa cabeza y extremidad remanente
    utilizando una única cámara.

    Los movimientos no se ejecutan
    directamente.

    Se publican como InteractionEvent.
    """

    def __init__(
        self,
        event_bus,
        mouse_controller,
        calibration_service,
        zoom_mode_manager=None,
        adaptive_parameters_manager=None
    ):
        self.event_bus = event_bus

        self.mouse = (
            mouse_controller
        )

        self.calibration = (
            calibration_service
        )

        if zoom_mode_manager is None:

            zoom_mode_manager = (
                ZoomModeManager()
            )

        self.zoom_mode_manager = (
            zoom_mode_manager
        )

        self.adaptive_parameters_manager = (
            adaptive_parameters_manager
        )

        self.profile = (
            calibration_service
            .get_profile()
        )

        self.face_tracker = (
            FaceTracker()
        )

        self.head_pose = (
            HeadPoseEstimator()
        )

        self.head_mapper = (
            HeadCursorMapper(
                sensitivity_x=(
                    self.profile
                    .sensitivity_x
                ),
                sensitivity_y=(
                    self.profile
                    .sensitivity_y
                ),
                dead_zone=(
                    self.profile
                    .dead_zone
                )
            )
        )

        self.head_zoom_detector = (
            HeadZoomDetector()
        )

        self.hand_tracker = (
            HandTracker()
        )

        self.gesture_detector = (
            GestureDetector()
        )

        self.limb_mapper = (
            LimbCursorMapper()
        )

        self.pose_history = deque(
            maxlen=30
        )

        self.range_samples = []

        self.range_calibration = False

        self.range_start_time = None

        self.last_neutral_calibration = 0.0

        self.last_range_calibration = 0.0

        self.calibration_cooldown = 3.0

        self.last_limb_position = None

        self.last_hand_seen_time = 0.0

        self.hand_release_delay = 0.40

        self.hand_smoothing = 0.35

        self.smoothed_hand_x = None
        self.smoothed_hand_y = None

        self.limb_min_step = 4

        self.hand_stable_frames = 0

        self.required_hand_frames = 3

    def _get_head_sensitivity_factor(
        self
    ):
        """
        Obtiene el factor adaptativo actual
        de sensibilidad de cabeza.
    
        Si el módulo adaptativo no está
        disponible o falla, se conserva
        el comportamiento original.
        """
    
        if (
            self.adaptive_parameters_manager
            is None
        ):
    
            return 1.0
    
        try:
        
            snapshot = (
                self.adaptive_parameters_manager
                .snapshot()
            )
    
            factor = float(
                snapshot
                .head_sensitivity_factor
            )
    
            if factor <= 0.0:
                return 1.0
    
            return factor
    
        except Exception:
        
            # El módulo adaptativo nunca debe
            # bloquear el control principal.
            return 1.0

    def _get_limb_sensitivity_factor(
        self
    ):
        """
        Obtiene el factor adaptativo actual
        de sensibilidad de la extremidad.

        Si la adaptación no está disponible
        o falla, mantiene el comportamiento
        original.
        """

        if (
            self.adaptive_parameters_manager
            is None
        ):

            return 1.0

        try:

            snapshot = (
                self.adaptive_parameters_manager
                .snapshot()
            )

            factor = float(
                snapshot
                .limb_sensitivity_factor
            )

            if factor <= 0.0:
                return 1.0

            return factor

        except Exception:

            return 1.0

    def _process_head(
        self,
        frame
    ):
        results = (
            self.face_tracker
            .process_frame(frame)
        )

        self.face_tracker.draw_landmarks(
            frame,
            results
        )

        landmarks = (
            self.face_tracker
            .get_landmarks(results)
        )

        if landmarks is None:

            self.head_mapper.reset()

            self.head_zoom_detector.reset()


            return

        height, width = (
            frame.shape[:2]
        )

        pose = (
            self.head_pose
            .estimate(
                landmarks,
                width,
                height
            )
        )

        if pose is None:

            self.head_zoom_detector.reset()

            return

        self.pose_history.append(
            pose
        )

        if self.range_calibration:
            
            self.head_zoom_detector.reset()

            self._process_range_calibration(
                pose
            )

            return

        if not self.profile.is_calibrated:

            self.head_zoom_detector.reset()

            return

        if (
            self.zoom_mode_manager
            .is_enabled()
        ):

            zoom_action = (
                self.head_zoom_detector
                .detect(
                    pitch=pose["pitch"],
                    neutral_pitch=(
                        self.profile
                        .neutral_pitch
                    )
                )
            )

            if zoom_action is not None:
            
                self.head_mapper.reset()

                self._publish_head_zoom(
                    zoom_action
                )

                return

            if (
                self.head_zoom_detector
                .is_active
            ):

                self.head_mapper.reset()

                return

        else:
        
            self.head_zoom_detector.reset()


        if self.head_zoom_detector.is_active:
        
            self.head_mapper.reset()

            return

        if self._limb_has_control():

            self.head_mapper.reset()

            return

        head_sensitivity_factor = (
            self._get_head_sensitivity_factor()
        )
        
        dx, dy = (
            self.head_mapper
            .calculate(
                pose["yaw"],
                pose["pitch"],
                self.profile.neutral_yaw,
                self.profile.neutral_pitch,
                sensitivity_factor=(
                    head_sensitivity_factor
                )
            )
        )

        if dx == 0 and dy == 0:
            return

        event = InteractionEvent(
            source=EventSource.HEAD,
            event_type=(
                EventType.CURSOR_MOVE
            ),
            payload={
                "mode": "relative",
                "dx": dx,
                "dy": dy
            },
            confidence=1.0,
            conflict_key="cursor"
        )

        self.event_bus.publish(
            event
        )

    def _publish_head_zoom(
        self,
        action
    ):

        if (
            action
            == SystemAction.ZOOM_IN
        ):

            print(
                "Gesto de cabeza reconocido: "
                "acercar"
            )

        elif (
            action
            == SystemAction.ZOOM_OUT
        ):

            print(
                "Gesto de cabeza reconocido: "
                "alejar"
            )

        else:

            return

        event = InteractionEvent(
            source=EventSource.HEAD,
            event_type=EventType.ACTION,
            action=action,
            confidence=1.0,
            conflict_key="action"
        )

        self.event_bus.publish(
            event
    )    

    def _publish_gesture(
        self,
        gesture,
        confidence
    ):
        """
        Convierte un gesto corporal
        en un evento multimodal.
        """

        action = None

        if (
            gesture
            == GestureDetector
            .GESTURE_DRAW
        ):

            action = (
                SystemAction.DRAW
            )

            print(
                "Gesto reconocido: "
                "dibujar"
            )

        elif (
            gesture
            == GestureDetector
            .GESTURE_ERASE
        ):

            action = (
                SystemAction.ERASE
            )

            print(
                "Gesto reconocido: "
                "borrar"
            )

        if action is None:
            return

        event = InteractionEvent(
            source=EventSource.GESTURE,
            event_type=EventType.ACTION,
            action=action,
            confidence=confidence,
            conflict_key="action"
        )

        self.event_bus.publish(
            event
        )

    def _process_limb(
        self,
        frame
    ):
        results = (
            self.hand_tracker
            .process_frame(frame)
        )

        selected_hand = (
            self.hand_tracker
            .get_selected_hand(
                results,
                self.profile
                .selected_limb
            )
        )

        if not selected_hand:

            self.hand_stable_frames = 0
        
            self.gesture_detector.reset()

            if not self._limb_has_control():
            
                self.limb_mapper.reset()

                self.last_limb_position = None

                self.smoothed_hand_x = None
                self.smoothed_hand_y = None

            return

        self.hand_stable_frames += 1

        if (
            self.hand_stable_frames
            < self.required_hand_frames
        ):
            return

        self.last_hand_seen_time = (
            time.monotonic()
        )

        hand_landmarks = (
            selected_hand[
                "landmarks"
            ]
        )

        gesture = (
            self.gesture_detector
            .detect(
                hand_landmarks
            )
        )
        
        if gesture is not None:
        
            self._publish_gesture(
                gesture,
                selected_hand[
                    "score"
                ]
            )

        self.hand_tracker.draw_hand(
            frame,
            hand_landmarks
        )

        hand_position = (
            self.hand_tracker
            .get_palm_center_position(
                hand_landmarks
            )
        )

        if hand_position is None:
            return

        (
            screen_left,
            screen_top,
            screen_width,
            screen_height
        ) = (
            self.mouse
            .get_virtual_screen_bounds()
        )

        raw_x = hand_position["x"]
        raw_y = hand_position["y"]

        if (
            self.smoothed_hand_x
            is None
        ):

            self.smoothed_hand_x = raw_x
            self.smoothed_hand_y = raw_y

        else:
        
            alpha = self.hand_smoothing

            self.smoothed_hand_x = (
                alpha * raw_x
                + (1 - alpha)
                * self.smoothed_hand_x
            )

            self.smoothed_hand_y = (
                alpha * raw_y
                + (1 - alpha)
                * self.smoothed_hand_y
            )

        limb_sensitivity_factor = (
            self._get_limb_sensitivity_factor()
        )
        
        cursor_x, cursor_y = (
            self.limb_mapper.calculate(
                self.smoothed_hand_x,
                self.smoothed_hand_y,
                screen_width,
                screen_height,
                sensitivity_factor=(
                    limb_sensitivity_factor
                )
            )
        )

        cursor_x = (
            cursor_x
            + screen_left
        )
        
        cursor_y = (
            cursor_y
            + screen_top
        )

        current_position = (
            cursor_x,
            cursor_y
        )

        if (
            self.last_limb_position
            is not None
        ):

            previous_x, previous_y = (
                self.last_limb_position
            )

            delta_x = abs(
                cursor_x
                - previous_x
            )

            delta_y = abs(
                cursor_y
                - previous_y
            )

            if (
                delta_x
                < self.limb_min_step
                and delta_y
                < self.limb_min_step
            ):

                return

        if (
            current_position
            == self.last_limb_position
        ):
            return

        self.last_limb_position = (
            current_position
        )

        confidence = (
            selected_hand[
                "score"
            ]
        )

        event = InteractionEvent(
            source=EventSource.LIMB,
            event_type=(
                EventType.CURSOR_MOVE
            ),
            payload={
                "mode": "absolute",
                "x": cursor_x,
                "y": cursor_y
            },
            confidence=confidence,
            conflict_key="cursor"
        )

        self.event_bus.publish(
            event
        )

    def _calibrate_neutral(self):

        if len(self.pose_history) < 10:

            print(
                "Mantén la cabeza quieta "
                "mirando al frente unos segundos."
            )

            return

        success = (
            self.calibration
            .calibrate_neutral(
                list(
                    self.pose_history
                )
            )
        )

        if success:

            self.profile = (
                self.calibration
                .get_profile()
            )

            self.head_mapper.reset()

            self.head_zoom_detector.reset()

            print("")
            print(
                "Posición neutra "
                "calibrada correctamente."
            )

            print(
                f"Yaw neutral: "
                f"{self.profile.neutral_yaw:.2f}"
            )

            print(
                f"Pitch neutral: "
                f"{self.profile.neutral_pitch:.2f}"
            )

            print(
                f"Roll neutral: "
                f"{self.profile.neutral_roll:.2f}"
            )

    def _start_range_calibration(self):

        self.range_samples = []

        self.range_calibration = True

        self.range_start_time = (
            time.time()
        )

        print("")
        print(
            "CALIBRACIÓN DE RANGO CERVICAL"
        )

        print(
            "Durante 5 segundos mueve "
            "lentamente la cabeza:"
        )

        print(
            "izquierda, derecha, "
            "arriba y abajo."
        )

    def _process_range_calibration(
        self,
        pose
    ):
        self.range_samples.append(
            pose
        )

        elapsed = (
            time.time()
            - self.range_start_time
        )

        if elapsed < 5:
            return

        self.calibration \
            .calibrate_cervical_range(
                self.range_samples
            )

        self.profile = (
            self.calibration
            .get_profile()
        )

        self.range_calibration = False

        print(
            "Rango cervical "
            "guardado correctamente."
        )

    def run(self):

        camera = cv2.VideoCapture(
            0,
            cv2.CAP_DSHOW
        )

        camera.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            1280
        )

        camera.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            720
        )

        camera.set(
            cv2.CAP_PROP_FPS,
            30
        )

        if not camera.isOpened():

            print(
                "ERROR: No se pudo abrir "
                "la cámara."
            )

            return

        print("")
        print(
            "CONTROL MULTIMODAL VISUAL"
        )
        print(
            "Cabeza + extremidad"
        )
        print("----------------------------")
        print(
            "C = calibrar posición neutra"
        )
        print(
            "R = calibrar rango cervical"
        )
        print(
            "Q = salir"
        )
        print("----------------------------")

        try:

            while True:

                success, frame = (
                    camera.read()
                )

                if not success:

                    print(
                        "ERROR: No se pudo "
                        "capturar el frame."
                    )

                    break

                frame = cv2.flip(
                    frame,
                    1
                )

                self._process_limb(
                    frame
                )

                self._process_head(
                    frame
                )

                cv2.putText(
                    frame,
                    (
                        "ZeroUI-AC - "
                        "Multimodal"
                    ),
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    (
                        "Extremidad: "
                        f"{self.profile.selected_limb}"
                    ),
                    (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    (
                        "C: neutral | "
                        "R: rango | "
                        "Q: salir"
                    ),
                    (20, 690),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                cv2.imshow(
                    (
                        "ZeroUI-AC - "
                        "Control multimodal"
                    ),
                    frame
                )

                key = (
                    cv2.waitKey(1)
                    & 0xFF
                )

                if key == ord("q"):
                    break

                current_time = (
                    time.time()
                )

                if key == ord("c"):

                    if (
                        current_time
                        - self.last_neutral_calibration
                        >= self.calibration_cooldown
                    ):

                        self.last_neutral_calibration = (
                            current_time
                        )

                        self._calibrate_neutral()

                if key == ord("r"):

                    if (
                        not self.range_calibration
                        and current_time
                        - self.last_range_calibration
                        >= self.calibration_cooldown
                    ):

                        self.last_range_calibration = (
                            current_time
                        )

                        self._start_range_calibration()

        finally:

            camera.release()

            self.face_tracker.close()

            self.hand_tracker.close()

            cv2.destroyAllWindows()

            print(
                "Control multimodal "
                "visual finalizado."
            )

    def _limb_has_control(self):
        """
        Mantiene temporalmente el control
        de la extremidad aunque MediaPipe
        pierda la mano durante unos frames.
        """

        elapsed = (
            time.monotonic()
            - self.last_hand_seen_time
        )

        return (
            elapsed
            <= self.hand_release_delay
        )