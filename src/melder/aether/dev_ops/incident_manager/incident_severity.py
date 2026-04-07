from enum import auto, Enum
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class IncidentSeverity(Enum):
    """
    Severity classification for incidents recorded by `IncidentManager`.

    Contract:
    - Values are ordered conceptually from lowest urgency to highest urgency.
    - The enum is descriptive only; higher-level tooling decides what policy or
      escalation behavior each level should trigger.

    Levels:
    - `info`: Informational event; no immediate action expected.
    - `warning`: Unexpected but not immediately blocking condition.
    - `error`: Actionable failure that should be investigated.
    - `critical`: Severe condition requiring immediate attention.
    """
    __melder_internal__ = _mrg.sentinel
    info = auto()
    warning = auto()
    error = auto()
    critical = auto()
