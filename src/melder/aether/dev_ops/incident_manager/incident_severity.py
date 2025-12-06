from enum import auto, Enum


class IncidentSeverity(Enum):
    """
    Severity levels for incidents recorded by IncidentManager.

    - info: Informational; no action required.
    - warning: Something unexpected but not blocking.
    - error: An actionable failure occurred.
    - critical: Severe condition requiring immediate attention.
    """
    info = auto()
    warning = auto()
    error = auto()
    critical = auto()
