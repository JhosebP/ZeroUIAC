from dataclasses import dataclass, asdict


@dataclass
class CalibrationProfile:
    """
    Almacena los parámetros obtenidos durante
    la calibración inicial de ZeroUI-AC.
    """

    # Posición neutra de la cabeza
    neutral_yaw: float = 0.0
    neutral_pitch: float = 0.0
    neutral_roll: float = 0.0

    # Sensibilidad del movimiento del cursor
    sensitivity_x: float = 2.0
    sensitivity_y: float = 2.0

    # Zona muerta para evitar movimientos involuntarios
    dead_zone: float = 2.0

    # Rango cervical
    cervical_yaw_min: float = 0.0
    cervical_yaw_max: float = 0.0

    cervical_pitch_min: float = 0.0
    cervical_pitch_max: float = 0.0

    # Configuración del micrófono
    microphone_gain: float = 1.0
    microphone_sample_rate: int = 16000

    # Extremidad seleccionada
    selected_limb: str = "derecha"

    # Estado de calibración
    is_calibrated: bool = False

    def to_dict(self):
        """
        Convierte el perfil a diccionario.
        """

        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        """
        Crea un perfil a partir de un diccionario.
        """

        return cls(**data)