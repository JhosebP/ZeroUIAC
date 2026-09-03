import time
from collections import deque

import cv2
import pyautogui

from modules.vision.face_tracker import (
    FaceTracker
)

from modules.vision.head_pose import (
    HeadPoseEstimator
)

from modules.vision.head_cursor_mapper import (
    HeadCursorMapper
)


class HeadControlService:
    """
    Coordina el control del cursor
    mediante movimientos de cabeza.
    """

    def __init__(
        self,
        mouse_controller,
        calibration_service
    ):

        self.mouse = mouse_controller

        self.calibration = calibration_service

        self.profile = (
            calibration_service.get_profile()
        )

        self.tracker = FaceTracker()

        self.head_pose = HeadPoseEstimator()

        self.mapper = HeadCursorMapper(
            sensitivity_x=(
                self.profile.sensitivity_x
            ),
            sensitivity_y=(
                self.profile.sensitivity_y
            ),
            dead_zone=(
                self.profile.dead_zone
            )
        )

        # Guarda las últimas posiciones de cabeza
        self.pose_history = deque(
            maxlen=30
        )

        # Datos para calibrar rango cervical
        self.range_samples = []

        self.range_calibration = False

        self.range_start_time = None

        self.last_neutral_calibration = 0.0
        self.last_range_calibration = 0.0
        self.calibration_cooldown = 3.0

    def run(self):
        """
        Inicia cámara y control por cabeza.
        """

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
                "ERROR: No se pudo abrir la cámara."
            )

            return

        print("")
        print("CONTROL POR CABEZA")
        print("----------------------------")
        print("C = calibrar posición neutra")
        print("R = calibrar rango cervical")
        print("Q = salir")
        print("----------------------------")

        try:

            while True:

                success, frame = camera.read()

                if not success:

                    print(
                        "ERROR: No se pudo capturar el frame."
                    )

                    break

                # Efecto espejo
                frame = cv2.flip(
                    frame,
                    1
                )

                results = (
                    self.tracker.process_frame(
                        frame
                    )
                )

                self.tracker.draw_landmarks(
                    frame,
                    results
                )

                landmarks = (
                    self.tracker.get_landmarks(
                        results
                    )
                )

                if landmarks is not None:

                    height, width = (
                        frame.shape[:2]
                    )

                    pose = (
                        self.head_pose.estimate(
                            landmarks,
                            width,
                            height
                        )
                    )

                    if pose is not None:

                        self.pose_history.append(
                            pose
                        )

                        self._process_pose(
                            pose
                        )

                        self._draw_information(
                            frame,
                            pose
                        )

                else:

                    # Si pierde el rostro,
                    # se detiene el movimiento.
                    self.mapper.reset()

                    cv2.putText(
                        frame,
                        "ROSTRO NO DETECTADO",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 0, 255),
                        2
                    )

                cv2.putText(
                    frame,
                    "C: neutral | R: rango | Q: salir",
                    (20, 690),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                cv2.imshow(
                    "ZeroUI-AC - Sprint 1",
                    frame
                )

                key = (
                    cv2.waitKey(1)
                    & 0xFF
                )

                if key == ord("q"):
                    break
                
                current_time = time.time()
                
                if key == ord("c"):
                    if (
                        current_time - self.last_neutral_calibration
                        >= self.calibration_cooldown
                    ):
                        self.last_neutral_calibration = current_time
                        self._calibrate_neutral()
                
                if key == ord("r"):
                    if (
                        not self.range_calibration
                        and current_time - self.last_range_calibration
                        >= self.calibration_cooldown
                    ):
                        self.last_range_calibration = current_time
                        self._start_range_calibration()
        finally:

            camera.release()

            self.tracker.close()

            cv2.destroyAllWindows()

    def _process_pose(self, pose):
        """
        Procesa los ángulos obtenidos.
        """

        # Si estamos calibrando rango cervical
        if self.range_calibration:

            self.range_samples.append(
                pose
            )

            elapsed = (
                time.time()
                - self.range_start_time
            )

            if elapsed >= 5:

                self.calibration.calibrate_cervical_range(
                    self.range_samples
                )

                self.range_calibration = False

                print(
                    "Rango cervical guardado correctamente."
                )

            return

        # No mover cursor hasta calibrar
        if not self.profile.is_calibrated:
            return

        dx, dy = self.mapper.calculate(
            pose["yaw"],
            pose["pitch"],
            self.profile.neutral_yaw,
            self.profile.neutral_pitch
        )

        try:

            self.mouse.move_relative(
                dx,
                dy
            )

        except pyautogui.FailSafeException:

            print(
                "FailSafe de PyAutoGUI activado."
            )

    def _calibrate_neutral(self):
        """
        Registra la posición neutra utilizando
        las últimas muestras capturadas.
        """

        if len(self.pose_history) < 10:

            print(
                "Mantén la cabeza quieta "
                "mirando al frente unos segundos."
            )

            return

        success = (
            self.calibration.calibrate_neutral(
                list(self.pose_history)
            )
        )

        if success:

            self.profile = (
                self.calibration.get_profile()
            )

            self.mapper.reset()

            print("")
            print(
                "Posición neutra calibrada correctamente."
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
        """
        Inicia la captura del rango cervical.
        """

        self.range_samples = []

        self.range_calibration = True

        self.range_start_time = time.time()

        print("")
        print(
            "CALIBRACIÓN DE RANGO CERVICAL"
        )

        print(
            "Durante 5 segundos mueve lentamente "
            "la cabeza:"
        )

        print(
            "izquierda, derecha, arriba y abajo."
        )

    def _draw_information(
        self,
        frame,
        pose
    ):
        """
        Muestra información sobre el video.
        """

        cv2.putText(
            frame,
            f"Yaw: {pose['yaw']:.2f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Pitch: {pose['pitch']:.2f}",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Roll: {pose['roll']:.2f}",
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )

        if self.profile.is_calibrated:

            cv2.putText(
                frame,
                "CALIBRADO",
                (20, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

        else:

            cv2.putText(
                frame,
                "PRESIONA C PARA CALIBRAR",
                (20, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

        if self.range_calibration:

            cv2.putText(
                frame,
                "MUEVE LA CABEZA EN TODAS LAS DIRECCIONES",
                (20, 180),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2
            )