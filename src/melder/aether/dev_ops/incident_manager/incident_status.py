from enum import auto, Enum


class IncidentStatus(Enum):
    """
    Lifecycle status for an incident.

    - open: Newly created, untriaged.
    - acknowledged: Seen/triaged but not resolved.
    - resolved: Underlying issue addressed.
    - suppressed: Muted/accepted; no further noise desired.
    """
    open = auto()
    acknowledged = auto()
    resolved = auto()
    suppressed = auto()
