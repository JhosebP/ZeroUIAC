import cv2
import numpy as np


class HeadPoseEstimator:
    """
    Estima la orientación de la cabeza:

    - yaw   : izquierda / derecha
    - pitch : arriba / abajo
    - roll  : inclinación lateral
    """

    LANDMARK_IDS = [1, 152, 33, 263, 61, 291]

    # Modelo 3D aproximado de un rostro humano
    MODEL_POINTS = np.array([
        (0.0, 0.0, 0.0),          # Nariz
        (0.0, -63.6, -12.5),      # Mentón
        (-43.3, 32.7, -26.0),     # Ojo izquierdo
        (43.3, 32.7, -26.0),      # Ojo derecho
        (-28.9, -28.9, -24.1),    # Boca izquierda
        (28.9, -28.9, -24.1),     # Boca derecha
    ], dtype=np.float64)

    @staticmethod
    def normalize_angle(angle):
        """
        Normaliza los ángulos para evitar valores
        cercanos a +180 o -180 grados.
        """

        if angle > 90:
            angle -= 180

        elif angle < -90:
            angle += 180

        return angle

    def estimate(self, landmarks, frame_width, frame_height):

        if landmarks is None:
            return None

        image_points = []

        for landmark_id in self.LANDMARK_IDS:
            landmark = landmarks[landmark_id]

            x = landmark.x * frame_width
            y = landmark.y * frame_height

            image_points.append((x, y))

        image_points = np.array(
            image_points,
            dtype=np.float64
        )

        # Matriz aproximada de la cámara
        focal_length = frame_width

        center = (
            frame_width / 2,
            frame_height / 2
        )

        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)

        distortion_coefficients = np.zeros(
            (4, 1),
            dtype=np.float64
        )

        success, rotation_vector, translation_vector = cv2.solvePnP(
            self.MODEL_POINTS,
            image_points,
            camera_matrix,
            distortion_coefficients,
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return None

        rotation_matrix, _ = cv2.Rodrigues(
            rotation_vector
        )

        angles, _, _, _, _, _ = cv2.RQDecomp3x3(
            rotation_matrix
        )

        pitch = self.normalize_angle(
            float(angles[0])
        )

        yaw = self.normalize_angle(
            float(angles[1])
        )

        roll = self.normalize_angle(
            float(angles[2])
        )

        return {
            "yaw": yaw,
            "pitch": pitch,
            "roll": roll,
            "rotation_vector": rotation_vector,
            "translation_vector": translation_vector
        }