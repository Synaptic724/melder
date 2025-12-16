from enum import auto, Enum
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class IncidentSeverity(Enum):
    """
    Severity levels for incidents recorded by IncidentManager.

    - info: Informational; no action required.
    - warning: Something unexpected but not blocking.
    - error: An actionable failure occurred.
    - critical: Severe condition requiring immediate attention.
    """
    __melder_internal__ = _mrg.sentinel
    info = auto()
    warning = auto()
    error = auto()
    critical = auto()
