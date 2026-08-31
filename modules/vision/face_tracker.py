import cv2
import mediapipe as mp

try:
    from .head_pose import HeadPoseEstimator
except ImportError:
    from head_pose import HeadPoseEstimator

class FaceTracker:
    def __init__(
        self,
        max_num_faces=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=max_num_faces,
            refine_landmarks=False,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def process_frame(self, frame):
        """
        Procesa un frame y devuelve los puntos faciales detectados.
        """

        # OpenCV trabaja en BGR.
        # MediaPipe necesita RGB.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        rgb_frame.flags.writeable = False

        results = self.face_mesh.process(rgb_frame)

        rgb_frame.flags.writeable = True

        return results

    def draw_landmarks(self, frame, results):
        """
        Dibuja la malla facial sobre el frame.
        """

        if not results.multi_face_landmarks:
            return frame

        for face_landmarks in results.multi_face_landmarks:

            # Dibuja la malla completa del rostro
            self.mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=(
                    self.mp_drawing_styles
                    .get_default_face_mesh_tesselation_style()
                )
            )

            # Dibuja contornos principales
            self.mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=(
                    self.mp_drawing_styles
                    .get_default_face_mesh_contours_style()
                )
            )

        return frame

    def get_landmarks(self, results):
        """
        Devuelve los landmarks del primer rostro detectado.
        """

        if not results.multi_face_landmarks:
            return None

        return results.multi_face_landmarks[0].landmark

    def close(self):
        """
        Libera los recursos de MediaPipe.
        """
        self.face_mesh.close()


def main():

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    camera.set(cv2.CAP_PROP_FPS, 30)

    if not camera.isOpened():
        print("ERROR: No se pudo abrir la cámara.")
        return

    tracker = FaceTracker()
    head_pose_estimator = HeadPoseEstimator()

    print("ZeroUI-AC - Face Tracker")
    print("Presiona Q para salir.")

    try:

        while True:

            success, frame = camera.read()

            if not success:
                print("ERROR: No se pudo capturar el frame.")
                break

            # Espejo para que el movimiento sea natural
            frame = cv2.flip(frame, 1)

            results = tracker.process_frame(frame)

            tracker.draw_landmarks(frame, results)

            landmarks = tracker.get_landmarks(results)

            if landmarks is not None:
            
                height, width = frame.shape[:2]

                pose = head_pose_estimator.estimate(
                    landmarks,
                    width,
                    height
                )

                cv2.putText(
                    frame,
                    "ROSTRO DETECTADO",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    f"Landmarks: {len(landmarks)}",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

                if pose is not None:
                
                    yaw = pose["yaw"]
                    pitch = pose["pitch"]
                    roll = pose["roll"]

                    cv2.putText(
                        frame,
                        f"Yaw: {yaw:.2f}",
                        (20, 120),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 0),
                        2
                    )

                    cv2.putText(
                        frame,
                        f"Pitch: {pitch:.2f}",
                        (20, 150),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 0),
                        2
                    )

                    cv2.putText(
                        frame,
                        f"Roll: {roll:.2f}",
                        (20, 180),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 0),
                        2
                    )

            else:
            
                cv2.putText(
                    frame,
                    "ROSTRO NO DETECTADO",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )

            cv2.imshow(
                "ZeroUI-AC - Face Tracker",
                frame
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:

        tracker.close()
        camera.release()
        cv2.destroyAllWindows()

        print("Face Tracker finalizado.")


if __name__ == "__main__":
    main()