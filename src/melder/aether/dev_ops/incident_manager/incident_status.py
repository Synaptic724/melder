from enum import auto, Enum


class IncidentStatus(Enum):
    open = auto()
    acknowledged = auto()
    resolved = auto()
    suppressed = auto()
