from enum import auto, Enum


class IncidentSeverity(Enum):
    info = auto()
    warning = auto()
    error = auto()
    critical = auto()
