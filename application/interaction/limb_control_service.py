import cv2
import pyautogui

from modules.vision.hand_tracker import (
    HandTracker
)

from modules.vision.limb_cursor_mapper import (
    LimbCursorMapper
)


class LimbControlService:
    """
    Gestiona el control del cursor mediante
    la extremidad superior remanente.
    """

    def __init__(
        self,
        mouse_controller,
        calibration_service
    ):
        self.mouse = mouse_controller

        self.calibration = (
            calibration_service
        )

        self.profile = (
            calibration_service
            .get_profile()
        )

        self.hand_tracker = (
            HandTracker()
        )

        self.mapper = (
            LimbCursorMapper()
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

        screen_width, screen_height = (
            self.mouse.get_screen_size()
        )

        print("")
        print(
            "CONTROL MEDIANTE EXTREMIDAD"
        )
        print("----------------------------")
        print(
            "Extremidad seleccionada:",
            self.profile.selected_limb
        )
        print("Q = salir")
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

                # Vista tipo espejo.
                frame = cv2.flip(
                    frame,
                    1
                )

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

                if selected_hand:

                    hand_landmarks = (
                        selected_hand[
                            "landmarks"
                        ]
                    )

                    self.hand_tracker.draw_hand(
                        frame,
                        hand_landmarks
                    )

                    wrist = (
                        self.hand_tracker
                        .get_wrist_position(
                            hand_landmarks
                        )
                    )

                    if wrist:

                        cursor_x, cursor_y = (
                            self.mapper.calculate(
                                wrist["x"],
                                wrist["y"],
                                screen_width,
                                screen_height
                            )
                        )

                        try:

                            self.mouse.move_to(
                                cursor_x,
                                cursor_y
                            )

                        except (
                            pyautogui
                            .FailSafeException
                        ):

                            print(
                                "FailSafe de "
                                "PyAutoGUI activado."
                            )

                    confidence = (
                        selected_hand[
                            "score"
                        ]
                    )

                    cv2.putText(
                        frame,
                        (
                            "EXTREMIDAD "
                            "DETECTADA"
                        ),
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0),
                        2
                    )

                    cv2.putText(
                        frame,
                        (
                            "Confianza: "
                            f"{confidence:.2f}"
                        ),
                        (20, 75),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 0),
                        2
                    )

                else:

                    self.mapper.reset()

                    cv2.putText(
                        frame,
                        (
                            "EXTREMIDAD "
                            "NO DETECTADA"
                        ),
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 0, 255),
                        2
                    )

                cv2.putText(
                    frame,
                    (
                        "Extremidad: "
                        f"{self.profile.selected_limb}"
                    ),
                    (20, 110),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    "Q: salir",
                    (20, 680),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                cv2.imshow(
                    (
                        "ZeroUI-AC - "
                        "Control por extremidad"
                    ),
                    frame
                )

                key = (
                    cv2.waitKey(1)
                    & 0xFF
                )

                if key == ord("q"):
                    break

        finally:

            camera.release()

            self.hand_tracker.close()

            cv2.destroyAllWindows()

            print(
                "Control mediante "
                "extremidad finalizado."
            )