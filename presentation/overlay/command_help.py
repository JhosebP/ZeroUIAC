"""Help content derived from the same phrases used by voice recognition."""

from application.interaction.dictation_service import DictationService
from domain.commands.system_actions import SystemAction
from modules.voice.voice_commands import (
    SYSTEM_CONTROL_COMMANDS, VOICE_ACTION_MAP, VOICE_COMMANDS, VOICE_MODE_COMMANDS,
)
from modules.vision.gesture_detector import GestureDetector


def get_command_catalog():
    """Structured catalog for consumers that do not render panel headings."""
    toggles = [
        phrase for phrase in VOICE_COMMANDS
        if VOICE_ACTION_MAP.get(phrase) in (SystemAction.DRAW, SystemAction.ERASE)
    ]
    modes = list(VOICE_MODE_COMMANDS)
    modes.extend(sorted(DictationService.EXIT_PHRASES))
    modes.extend(f'{phrase} (alterna el modo)' for phrase in toggles)
    execution = [phrase for phrase in VOICE_COMMANDS if phrase not in toggles]
    physical = [
        'CABEZA',
        'Mover cabeza: controlar cursor',
        'Adelante: acercar (modo zoom)',
        'Atrás: alejar (modo zoom)',
        '', 'EXTREMIDAD',
        'Mover extremidad: controlar cursor',
        '', 'GESTOS DE MANO',
    ]
    gestures = {
        GestureDetector.GESTURE_DRAW: 'Índice y medio: alternar dibujo',
        GestureDetector.GESTURE_ERASE: 'Índice, medio y anular: alternar borrador',
    }
    physical.extend(gestures.values())
    physical.append('Mantener brevemente; soltar para repetir')
    return {
        'modes': modes,
        'execution': execution,
        'system': list(SYSTEM_CONTROL_COMMANDS),
        'gestures': physical,
    }


def get_command_groups():
    catalog = get_command_catalog()
    return (
        ('MODOS Y CONTROLES', catalog['modes'] + ['', 'CONTROLES ZEROUI', *catalog['system']]),
        ('EJECUCIÓN', catalog['execution']),
        ('GESTOS Y MOVIMIENTOS', catalog['gestures']),
    )
