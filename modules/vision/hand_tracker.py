import cv2
import mediapipe as mp


class HandTracker:
    """
    Detecta las manos del usuario mediante MediaPipe Hands.

    Permite seleccionar la mano/extremidad que será utilizada
    para controlar ZeroUI-AC.
    """

    def __init__(
        self,
        max_num_hands=2,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    ):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def process_frame(self, frame):
        """
        Procesa un frame BGR de OpenCV.
        """

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        rgb_frame.flags.writeable = False

        results = self.hands.process(
            rgb_frame
        )

        rgb_frame.flags.writeable = True

        return results

    def get_selected_hand(
        self,
        results,
        selected_limb="derecha"
    ):
        """
        Devuelve únicamente la mano seleccionada
        durante la calibración.

        selected_limb:
        - derecha
        - izquierda
        """

        if not results.multi_hand_landmarks:
            return None

        if not results.multi_handedness:
            return None

        selected_limb = selected_limb.lower()

        desired_label = (
            "right"
            if selected_limb == "derecha"
            else "left"
        )

        for hand_landmarks, handedness in zip(
            results.multi_hand_landmarks,
            results.multi_handedness
        ):
            classification = (
                handedness.classification[0]
            )

            label = classification.label.lower()
            score = classification.score

            if label == desired_label:
                return {
                    "landmarks": hand_landmarks,
                    "label": label,
                    "score": score
                }

        return None

    def get_wrist_position(
        self,
        hand_landmarks
    ):
        """
        Obtiene la posición normalizada X/Y
        de la muñeca.
        """

        if hand_landmarks is None:
            return None

        wrist_index = (
            self.mp_hands
            .HandLandmark
            .WRIST
            .value
        )

        wrist = (
            hand_landmarks
            .landmark[wrist_index]
        )

        return {
            "x": wrist.x,
            "y": wrist.y,
            "z": wrist.z
        }

    def get_palm_center_position(
        self,
        hand_landmarks
    ):
        """
        Obtiene el centro aproximado de la palma.
    
        Promedia muñeca y bases de los dedos
        para obtener una posición más estable.
        """
    
        if hand_landmarks is None:
            return None
    
        landmark_ids = [
            0,   # muñeca
            5,   # índice MCP
            9,   # medio MCP
            13,  # anular MCP
            17   # meñique MCP
        ]
    
        points = [
            hand_landmarks.landmark[
                landmark_id
            ]
            for landmark_id
            in landmark_ids
        ]
    
        x = sum(
            point.x
            for point in points
        ) / len(points)
    
        y = sum(
            point.y
            for point in points
        ) / len(points)
    
        z = sum(
            point.z
            for point in points
        ) / len(points)
    
        return {
            "x": x,
            "y": y,
            "z": z
        }

    def draw_hand(
        self,
        frame,
        hand_landmarks
    ):
        """
        Dibuja los landmarks de la mano.
        """

        if hand_landmarks is None:
            return frame

        self.mp_drawing.draw_landmarks(
            frame,
            hand_landmarks,
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_drawing_styles
            .get_default_hand_landmarks_style(),
            self.mp_drawing_styles
            .get_default_hand_connections_style()
        )

        return frame

    def close(self):
        self.hands.close()