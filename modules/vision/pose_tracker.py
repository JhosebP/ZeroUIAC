import cv2
import mediapipe as mp


class PoseTracker:
    """
    Rastrea la postura corporal mediante MediaPipe Pose.

    Se utilizará principalmente para obtener:
    - hombro;
    - codo;
    - muñeca;

    de la extremidad superior seleccionada.
    """

    def __init__(
        self,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    ):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = (
            mp.solutions.drawing_utils
        )

        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=(
                min_detection_confidence
            ),
            min_tracking_confidence=(
                min_tracking_confidence
            )
        )

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        rgb_frame.flags.writeable = False

        results = self.pose.process(
            rgb_frame
        )

        rgb_frame.flags.writeable = True

        return results

    def get_selected_limb(
        self,
        results,
        selected_limb="derecha"
    ):
        """
        Obtiene hombro, codo y muñeca
        de la extremidad seleccionada.
        """

        if not results.pose_landmarks:
            return None

        landmarks = (
            results.pose_landmarks.landmark
        )

        selected_limb = selected_limb.lower()

        if selected_limb == "derecha":

            shoulder_id = (
                self.mp_pose
                .PoseLandmark
                .RIGHT_SHOULDER
                .value
            )

            elbow_id = (
                self.mp_pose
                .PoseLandmark
                .RIGHT_ELBOW
                .value
            )

            wrist_id = (
                self.mp_pose
                .PoseLandmark
                .RIGHT_WRIST
                .value
            )

        else:

            shoulder_id = (
                self.mp_pose
                .PoseLandmark
                .LEFT_SHOULDER
                .value
            )

            elbow_id = (
                self.mp_pose
                .PoseLandmark
                .LEFT_ELBOW
                .value
            )

            wrist_id = (
                self.mp_pose
                .PoseLandmark
                .LEFT_WRIST
                .value
            )

        shoulder = landmarks[shoulder_id]
        elbow = landmarks[elbow_id]
        wrist = landmarks[wrist_id]

        return {
            "shoulder": shoulder,
            "elbow": elbow,
            "wrist": wrist
        }

    def draw_landmarks(
        self,
        frame,
        results
    ):
        if not results.pose_landmarks:
            return frame

        self.mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            self.mp_pose.POSE_CONNECTIONS
        )

        return frame

    def close(self):
        self.pose.close()