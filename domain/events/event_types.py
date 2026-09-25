from enum import Enum


class EventSource(str, Enum):
    """
    Identifica el canal que produjo un evento
    dentro de ZeroUI-AC.
    """

    VOICE = "voice"
    HEAD = "head"
    LIMB = "limb"
    GESTURE = "gesture"
    SYSTEM = "system"


class EventType(str, Enum):
    """
    Define el tipo general del evento.
    """

    ACTION = "action"
    CURSOR_MOVE = "cursor_move"
    GESTURE = "gesture"
    STATUS = "status"