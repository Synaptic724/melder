from enum import auto, Enum
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class IncidentStatus(Enum):
    """
    Lifecycle status for an incident.

    - open: Newly created, untriaged.
    - acknowledged: Seen/triaged but not resolved.
    - resolved: Underlying issue addressed.
    - suppressed: Muted/accepted; no further noise desired.
    """
    __melder_internal__ = _mrg.sentinel
    open = auto()
    acknowledged = auto()
    resolved = auto()
    suppressed = auto()
