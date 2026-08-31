from statistics import mean

from infrastructure.persistence.configuration_repository import (
    ConfigurationRepository
)


class CalibrationService:
    """
    Gestiona la calibración inicial del usuario.
    """

    def __init__(self):

        self.repository = ConfigurationRepository()

        self.profile = self.repository.load()

    def calibrate_neutral(self, samples):
        """
        Calcula la posición neutra de la cabeza
        utilizando varias muestras.
        """

        if not samples:
            return False

        self.profile.neutral_yaw = mean(
            sample["yaw"]
            for sample in samples
        )

        self.profile.neutral_pitch = mean(
            sample["pitch"]
            for sample in samples
        )

        self.profile.neutral_roll = mean(
            sample["roll"]
            for sample in samples
        )

        self.profile.is_calibrated = True

        self.repository.save(
            self.profile
        )

        return True

    def calibrate_cervical_range(self, samples):
        """
        Registra los límites aproximados
        del movimiento cervical.
        """

        if not samples:
            return False

        yaw_values = [
            sample["yaw"]
            for sample in samples
        ]

        pitch_values = [
            sample["pitch"]
            for sample in samples
        ]

        self.profile.cervical_yaw_min = min(
            yaw_values
        )

        self.profile.cervical_yaw_max = max(
            yaw_values
        )

        self.profile.cervical_pitch_min = min(
            pitch_values
        )

        self.profile.cervical_pitch_max = max(
            pitch_values
        )

        self.repository.save(
            self.profile
        )

        return True

    def set_microphone_gain(self, gain):
        """
        Guarda la sensibilidad inicial
        del micrófono.
        """

        self.profile.microphone_gain = gain

        self.repository.save(
            self.profile
        )

    def set_selected_limb(self, limb):
        """
        Establece qué extremidad será rastreada.
        """

        if limb not in (
            "izquierda",
            "derecha"
        ):
            return False

        self.profile.selected_limb = limb

        self.repository.save(
            self.profile
        )

        return True

    def get_profile(self):
        """
        Devuelve el perfil de calibración actual.
        """

        return self.profile